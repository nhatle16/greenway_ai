from langchain.tools import tool


@tool
def update_user_profile(
    username: str | None = None,
    language: str | None = None
) -> str:
    """Updates the user's name and/or preferred language in the system state."""
    updates = []
    if username:
        updates.append(f"user_name='{username}'")
    if language:
        updates.append(f"language='{language}'")

    if not updates:
        return "No updates provided."

    return f"Successfully updated profile: {', '.join(updates)}"
