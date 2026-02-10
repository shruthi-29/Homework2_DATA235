from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import supervisor_node, planner_node, reviewer_node
from .router import router_logic


def build_workflow():
    g = StateGraph(AgentState)

    g.add_node("supervisor", supervisor_node)
    g.add_node("planner", planner_node)
    g.add_node("reviewer", reviewer_node)

    g.set_entry_point("supervisor")

    g.add_conditional_edges(
        "supervisor",
        router_logic,
        {"planner": "planner", "reviewer": "reviewer", "END": END},
    )

    g.add_edge("planner", "supervisor")
    g.add_edge("reviewer", "supervisor")

    return g.compile()


# -------------------------
# Pretty-print helpers
# -------------------------

_NODE_LABEL = {
    "supervisor": "Supervisor",
    "planner": "Planner",
    "reviewer": "Reviewer",
}


def _extract_single_event(event: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    LangGraph stream events commonly look like:
      {"node_name": {"updated_key": value, ...}}
    This helper returns (node_name, updates_dict).
    """
    if not event:
        return ("", {})
    if len(event) != 1:
        # In case the engine returns more than one node update in one event,
        # pick them in order deterministically (rare).
        node_name = sorted(event.keys())[0]
        return (node_name, event[node_name] or {})
    node_name = next(iter(event.keys()))
    return (node_name, event[node_name] or {})


def _safe_get(d: Any, *keys: str, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _print_node_event(node: str, updates: Dict[str, Any], state_after: AgentState):
    label = _NODE_LABEL.get(node, node)
    print(f"--- {label} Node ---")
    print(f"[{node}] updated state keys: {list(updates.keys())}")

    if node == "planner":
        feedback = state_after.get("reviewer_feedback") or None
        proposal = state_after.get("planner_proposal") or None

        print(f"  Feedback: {feedback if feedback else None}")

        tags = _safe_get(proposal, "data", "tags")
        plan = _safe_get(proposal, "data", "plan")
        summary = _safe_get(proposal, "data", "summary")

        if isinstance(plan, list):
            print(f"  Proposal: {plan}")
        elif isinstance(tags, list):
            print(f"  Proposal: {tags}")
        else:
            print(f"  Proposal: {proposal}")

        if summary:
            print(f"  Summary: {summary}")


    if node == "reviewer":
        feedback = state_after.get("reviewer_feedback") or None
        # Prefer an "ok" field if your reviewer uses one, else infer from issues if present
        ok = _safe_get(feedback, "ok")
        issues = _safe_get(feedback, "data", "issues")

        if ok is None and isinstance(issues, list):
            ok = (len(issues) == 0)

        if feedback is not None:
            print(f"  Feedback: {feedback}")
        if ok is not None:
            print(f"  Reviewer OK: {ok}")


def run_once(initial_state: AgentState) -> AgentState:
    """
    Runs the graph once, prints a nice trace, and returns the final state.
    """
    app = build_workflow()

    print(f"\n--- Starting Graph Run [Strict: {bool(initial_state.get('strict', False))}] ---")

    # IMPORTANT: app.stream(initial_state) does not mutate your local dict in-place.
    # We'll maintain our own 'state_after' as we apply update patches as they stream in.
    state_after: AgentState = dict(initial_state)  # shallow copy

    for event in app.stream(initial_state):
        node, updates = _extract_single_event(event)

        # Apply updates to our local "state_after"
        if isinstance(updates, dict):
            state_after.update(updates)

        _print_node_event(node, updates, state_after)

    # Get authoritative final state from the graph engine
    final_state: AgentState = app.invoke(initial_state)

    print("\n--- Final State ---")
    print(f"Turn Count: {final_state.get('turn_count')}")
    feedback = final_state.get("reviewer_feedback") or {}
    ok = feedback.get("ok")
    if ok is None:
        issues = _safe_get(feedback, "data", "issues", default=[])
        ok = (isinstance(issues, list) and len(issues) == 0)
    print(f"Reviewer OK: {ok}")
    print("\n==============================\n")

    return final_state


def main():
    """
    Kept for backwards compatibility if you run `python -m agent_graph.workflow`.
    You can also call run_once() from run.py with different strict values.
    """
    state: AgentState = {
        "title": "Demo",
        "content": "Demo content",
        "email": "demo@example.com",
        "strict": False,
        "task": "Demo task",
        "planner_proposal": {},
        "reviewer_feedback": {},
        "turn_count": 0,
    }
    run_once(state)
