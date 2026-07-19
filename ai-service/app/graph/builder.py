"""Graph topology:

classify → (retrieve_docs ∥ retrieve_tickets) → troubleshoot → escalate
  → conditional: assistant channel + SOLVED (and not force_ticket) → summarize
  → otherwise → api_agent → summarize → END

"Create ticket anyway" resumes a finished SOLVED checkpoint: the API updates
state (force_ticket=True) as-if node "escalate" just ran, then continues the
graph, which now routes through api_agent.
"""

from langgraph.graph import END, START, StateGraph

from app.graph.nodes.api_agent import api_agent
from app.graph.nodes.classify import classify
from app.graph.nodes.escalate import escalate
from app.graph.nodes.retrieve_docs import retrieve_docs
from app.graph.nodes.retrieve_tickets import retrieve_tickets
from app.graph.nodes.summarize import summarize
from app.graph.nodes.troubleshoot import troubleshoot
from app.graph.state import HelpdeskState

NODE_ORDER = [
    "classify",
    "retrieve_docs",
    "retrieve_tickets",
    "troubleshoot",
    "escalate",
    "api_agent",
    "summarize",
]

_checkpointer = None
_graph = None


def route_after_escalate(state: HelpdeskState) -> str:
    if state.get("force_ticket"):
        return "api_agent"
    outcome = (state.get("escalation") or {}).get("outcome")
    if state.get("channel") == "assistant" and outcome == "SOLVED":
        return "summarize"
    return "api_agent"


def build_graph(checkpointer=None):
    graph = StateGraph(HelpdeskState)
    graph.add_node("classify", classify)
    graph.add_node("retrieve_docs", retrieve_docs)
    graph.add_node("retrieve_tickets", retrieve_tickets)
    graph.add_node("troubleshoot", troubleshoot)
    graph.add_node("escalate", escalate)
    graph.add_node("api_agent", api_agent)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve_docs")
    graph.add_edge("classify", "retrieve_tickets")
    graph.add_edge(["retrieve_docs", "retrieve_tickets"], "troubleshoot")
    graph.add_edge("troubleshoot", "escalate")
    graph.add_conditional_edges(
        "escalate",
        route_after_escalate,
        {"summarize": "summarize", "api_agent": "api_agent"},
    )
    graph.add_edge("api_agent", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile(checkpointer=checkpointer)


def set_checkpointer(checkpointer) -> None:
    """Called from the app lifespan once the Postgres saver is ready."""
    global _checkpointer, _graph
    _checkpointer = checkpointer
    _graph = None


def get_graph():
    """Process-wide compiled graph. Falls back to an in-memory checkpointer so
    the pipeline (and tests) work without Postgres — resume just won't survive
    a restart."""
    global _graph, _checkpointer
    if _graph is None:
        if _checkpointer is None:
            from langgraph.checkpoint.memory import MemorySaver

            _checkpointer = MemorySaver()
        _graph = build_graph(_checkpointer)
    return _graph
