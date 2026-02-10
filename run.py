import argparse
from agent_graph.workflow import run_once
from agent_graph.state import AgentState


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    state: AgentState = {
        "title": args.title,
        "content": args.content,
        "email": "demo@example.com",
        "strict": args.strict,
        "task": "Demo task",
        "planner_proposal": {},
        "reviewer_feedback": {},
        "turn_count": 0,
    }

    run_once(state)


if __name__ == "__main__":
    main()
