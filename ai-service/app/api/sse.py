"""Server-sent-events helpers: frame formatting plus a 15s heartbeat merged
into any event stream so proxies don't drop idle connections."""

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

HEARTBEAT_SECONDS = 15.0

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # disable proxy buffering (nginx et al.)
}


def format_sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


HEARTBEAT_FRAME = ": heartbeat\n\n"


async def with_heartbeat(
    events: AsyncIterator[str], interval: float = HEARTBEAT_SECONDS
) -> AsyncIterator[str]:
    """Re-yields `events`, inserting comment heartbeats during quiet periods."""
    iterator = events.__aiter__()
    pending: asyncio.Task | None = None
    try:
        while True:
            if pending is None:
                pending = asyncio.ensure_future(anext(iterator))
            done, _ = await asyncio.wait({pending}, timeout=interval)
            if not done:
                yield HEARTBEAT_FRAME
                continue
            try:
                frame = pending.result()
            except StopAsyncIteration:
                return
            finally:
                pending = None
            yield frame
    finally:
        if pending is not None:
            pending.cancel()
