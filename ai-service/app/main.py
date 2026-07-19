import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.queue import get_queue
from app.api import routes_admin, routes_analyze, routes_assist
from app.config import get_settings
from app.db.session import dispose_engine, get_engine
from app.graph.builder import set_checkpointer
from app.jobs import register_handlers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


async def _index_tickets_startup() -> None:
    """Best-effort startup indexing of resolved tickets; never blocks startup."""
    from app.rag.ticket_indexer import index_resolved_tickets

    await asyncio.sleep(5)  # give ticket-service a moment on cold compose starts
    try:
        counts = await index_resolved_tickets()
        logger.info("startup ticket indexing: %s", counts)
    except Exception as exc:
        logger.warning("startup ticket indexing skipped: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    checkpointer_ctx = None
    index_task: asyncio.Task | None = None

    # LangGraph checkpointer on ai_db (falls back to in-memory if unavailable,
    # e.g. during tests without Postgres).
    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        checkpointer_ctx = AsyncPostgresSaver.from_conn_string(settings.sync_database_url)
        checkpointer = await checkpointer_ctx.__aenter__()
        await checkpointer.setup()
        set_checkpointer(checkpointer)
        logger.info("Postgres checkpointer ready")
    except Exception as exc:
        checkpointer_ctx = None
        logger.warning("Postgres checkpointer unavailable (%s); using in-memory saver", exc)

    try:
        get_engine()
        register_handlers()
        get_queue().start_worker()
        index_task = asyncio.create_task(_index_tickets_startup())
    except Exception as exc:
        logger.warning("degraded startup: %s", exc)

    yield

    if index_task is not None:
        index_task.cancel()
    await get_queue().stop_worker()
    if checkpointer_ctx is not None:
        try:
            await checkpointer_ctx.__aexit__(None, None, None)
        except Exception:
            pass
    await dispose_engine()


app = FastAPI(title="ai-service", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_assist.router)
app.include_router(routes_analyze.router)
app.include_router(routes_admin.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
