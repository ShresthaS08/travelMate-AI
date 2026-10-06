from langchain_core.messages import HumanMessage

from app.nodes.reasoning import reasoning_node


state = {
    "messages": [
        HumanMessage(
            content=(
                "Plan a trip from Delhi to Goa "
                "from 2026-11-10 to 2026-11-15 "
                "for 2 people with a budget of 50000. "
                "I like beaches and good food."
            )
        )
    ],

    # Travel information
    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": ["beaches", "good food"],

    # Reasoning decision
    "decision_type": None,
    "decision_content": None,

    # Tool information
    "tool_name": None,
    "tool_args": {},
    "tool_result": None,

    # Booking information
    "selected_flight": None,
    "selected_hotel": None,
    "selected_activities": [],

    # Itinerary
    "itinerary": None,

    # Human approval
    "requires_approval": False,
    "approval_status": None,

    # Error handling
    "error": None,

    # Execution tracking
    "step_count": 0,
}


result = reasoning_node(state)


print("\n========== AI RESPONSE ==========\n")
print(result["messages"][0].content)


print("\n========== DECISION ==========\n")

print("Decision:", result["decision_type"])

print("Tool:", result["tool_name"])

print("Arguments:", result["tool_args"])

print("Content:", result["decision_content"])


print("\nSteps:", result["step_count"])