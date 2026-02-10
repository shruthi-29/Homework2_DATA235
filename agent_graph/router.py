from .tools import issues_from_feedback

MAX_TURNS = 5

def router_logic(state):
    if not state.get("planner_proposal"):
        return "planner"
    if not state.get("reviewer_feedback"):
        return "reviewer"

    issues = issues_from_feedback(state.get("reviewer_feedback", {}))
    if issues and state.get("turn_count", 0) < MAX_TURNS:
        return "planner"

    return "END"
