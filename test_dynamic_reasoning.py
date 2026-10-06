from app.nodes.reasoning import reasoning_node


test_state = {
    "messages": [],
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


result = reasoning_node(test_state)

print("\n========== FINAL REASONING RESULT ==========\n")
print(result)