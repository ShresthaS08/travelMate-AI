from langchain_core.messages import HumanMessage

from app.nodes.reasoning import reasoning_node
from app.nodes.tool_executor import tool_executor_node


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

    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": ["beaches", "good food"],

    "decision_type": None,
    "decision_content": None,

    "tool_name": None,
    "tool_args": {},
    "tool_result": None,

    "selected_flight": None,
    "selected_hotel": None,
    "selected_activities": [],

    "itinerary": None,

    "requires_approval": False,
    "approval_status": None,

    "error": None,

    "step_count": 0,
}


# STEP 1 — Ask the LLM what to do
reasoning_result = reasoning_node(state)

state.update(reasoning_result)

print("\n========== REASONING ==========\n")

print("Decision:", state["decision_type"])
print("Tool:", state["tool_name"])
print("Arguments:", state["tool_args"])


# STEP 2 — Execute the requested tool
tool_result = tool_executor_node(state)

state.update(tool_result)


print("\n========== TOOL RESULT ==========\n")

print(state["tool_result"])

print("\n========== ERROR ==========\n")

print(state["error"])

print("\nSteps:", state["step_count"])