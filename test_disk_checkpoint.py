from app.graph import travelmate_graph


print("\n================================================")
print("       DISK CHECKPOINT TEST")
print("================================================")


config = {
    "configurable": {
        "thread_id": "disk-test-001"
    }
}


initial_state = {
    "messages": [],

    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": ["beach", "food"],
    "booking_requested": False,

    "decision_type": None,
    "decision_content": None,

    "tool_name": None,
    "tool_args": {},
    "tool_result": None,
    "tool_results": {},

    "executed_tools": [
        "search_flights",
        "search_hotels"
    ],

    "selected_flight": None,
    "selected_hotel": None,
    "selected_activities": [],

    "itinerary": None,

    "requires_approval": False,
    "approval_status": None,
    "pending_action": None,

    "error": None,
    "step_count": 1,
}


print("\nSaving state to SQLite...")

travelmate_graph.update_state(
    config,
    initial_state
)


print("State saved.")


print("\nReading checkpoint back...")

checkpoint = travelmate_graph.get_state(config)


saved_state = checkpoint.values


print("\nCheckpointed destination:")
print(saved_state["destination"])


print("\nCheckpointed step count:")
print(saved_state["step_count"])


print("\nCheckpointed executed tools:")
print(saved_state["executed_tools"])


print("\n================================================")
print("        DISK CHECKPOINT TEST COMPLETE")
print("================================================")