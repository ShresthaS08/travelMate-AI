from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Conversation
    messages: Annotated[list[BaseMessage], add_messages]

    # Travel requirements
    origin: str | None
    destination: str | None
    start_date: str | None
    end_date: str | None
    passengers: int
    budget: float | None
    preferences: list[str]

    # Reasoning decision
    decision_type: str | None
    decision_content: str | None

    # Tool execution
    tool_name: str | None
    tool_args: dict
    tool_result: dict | None
    tool_results: dict
    executed_tools: list[str]

    # Booking
    selected_flight: dict | None
    selected_hotel: dict | None
    selected_activities: list[dict]

    # Itinerary
    itinerary: dict | None

    # Human approval
    requires_approval: bool
    approval_status: str | None
    pending_action: dict | None

    # Error handling
    error: str | None

    # Execution tracking
    step_count: int