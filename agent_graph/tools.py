def issues_from_feedback(feedback):
    data = feedback.get("data", {}) if feedback else {}
    issues = data.get("issues", [])
    return issues if isinstance(issues, list) else []
