from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    messages: List[str]
    intent: Optional[str]
    current_field: str | None
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]
    plan: Optional[str]
    name_confirmed: bool
    email_confirmed: bool
    platform_confirmed: bool