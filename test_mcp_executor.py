from app.nodes.tool_executor import tool_executor_node


test_state = {
    "messages": [],
    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": ["beaches", "good food"],

    "decision_type": "TOOL_REQUEST",
    "decision_content": None,

    "tool_name": "search_flights",
    "tool_args": {
        "origin": "Delhi",
        "destination": "Goa",
        "date": "2026-11-10",
        "passengers": 2
    },

    "tool_result": None,
    "executed_tools": [],

    "selected_flight": None,
    "selected_hotel": None,
    "selected_activities": [],

    "itinerary": None,

    "requires_approval": False,
    "approval_status": None,

    "error": None,
    "step_count": 0
}


result = tool_executor_node(test_state)

print("\n========== FINAL EXECUTOR RESULT ==========\n")

print(result)