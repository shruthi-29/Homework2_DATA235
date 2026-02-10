from typing import Dict, Any
import re
from collections import Counter
from .state import AgentState

_STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while",
    "to","of","in","on","for","with","as","by","at","from","into","about",
    "it","this","that","these","those","is","are","was","were","be","been","being",
    "can","could","should","would","will","may","might","must","do","does","did",
    "how","what","why","who","whom","which",
    "we","you","they","i","he","she","them","us","our","your","their",
}

def _normalize_token(t: str) -> str:
    #plural normalization
    if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Supervisor node: increments turn counter only."""
    turn = int(state.get("turn_count", 0)) + 1
    return {"turn_count": turn}


def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner node (heuristic): derives tags and a one-sentence summary
    from title+content. Returns {'planner_proposal': {...}}.
    """
    title = state.get("title", "") or ""
    content = state.get("content", "") or ""
    text = f"{title} {content}".lower()

    tokens = re.findall(r"[a-z0-9]+", text)
    tokens = [t for t in tokens if len(t) >= 4 and t not in _STOPWORDS]
    tokens = [_normalize_token(t) for t in tokens]

    counts = Counter(tokens)
    tags = []
    for w, _ in counts.most_common(20):
        if w not in tags:
            tags.append(w)
        if len(tags) == 3:
            break
    while len(tags) < 3:
        tags.append(f"tag{len(tags)+1}")

    # basic summary
    first_sentence = ""
    if content:
        parts = re.split(r"[.!?]\s+", content.strip())
        if parts and parts[0]:
            first_sentence = parts[0].strip()
    if not first_sentence:
        first_sentence = title.strip() or "Auto-generated summary."

    words = first_sentence.split()
    if len(words) > 25:
        summary = " ".join(words[:25]) + "..."
    else:
        summary = first_sentence

    proposal = {
        "data": {
            "tags": tags,
            "summary": summary,
            "issues": []
        }
    }
    return {"planner_proposal": proposal}


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    proposal = state.get("planner_proposal", {}) or {}
    issues = []

    #Test-only hook: if caller set this flag, force an issue
    if state.get("force_reviewer_issue"):
        issues.append("Forced issue for loop testing")

    tags = []
    if isinstance(proposal, dict):
        tags = proposal.get("data", {}).get("tags", [])
    if not isinstance(tags, list) or len(tags) < 3:
        issues.append("Planner must provide 3 tags")

    summary = proposal.get("data", {}).get("summary") if isinstance(proposal, dict) else None
    if not summary:
        issues.append("Planner must provide a one-sentence summary")

    feedback = {"data": {"issues": issues}}
    feedback["ok"] = (len(issues) == 0)
    return {"reviewer_feedback": feedback}
