from app.state import AgentState


state: AgentState = {
    "messages": [],

    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": ["beaches", "good food"],

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


print("TravelMate state created successfully!")
print("Destination:", state["destination"])
print("Budget:", state["budget"])
print("Passengers:", state["passengers"])