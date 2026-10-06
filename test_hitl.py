from langgraph.types import Command

from app.graph import travelmate_graph


# ============================================================
# TEST STATE
# ============================================================

initial_state = {
    "messages": [],

    # Travel requirements
    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": [
        "beaches",
        "relaxation"
    ],
    "booking_requested": True,

    # Reasoning
    "decision_type": "APPROVAL_REQUIRED",
    "decision_content": (
        "Human approval is required before booking the trip."
    ),

    # Tool
    "tool_name": "book_trip",
    "tool_args": {
        "flight_id": "F001",
        "hotel_id": "H002",
        "passengers": 2,
        "destination": "Goa"
    },
    "tool_result": None,
    "tool_results": {
        "search_flights": {
            "status": "success",
            "flights": [
                {
                    "flight_id": "F001",
                    "airline": "IndiGo",
                    "departure": "08:00",
                    "arrival": "10:30",
                    "price": 4500
                }
            ]
        },
        "search_hotels": {
            "status": "success",
            "hotels": [
                {
                    "hotel_id": "H002",
                    "name": "Palm Paradise Hotel",
                    "price_per_night": 2800,
                    "rating": 4.2
                }
            ]
        }
    },
    "executed_tools": [
        "search_flights",
        "search_hotels"
    ],

    # Booking
    "selected_flight": {
        "flight_id": "F001",
        "airline": "IndiGo",
        "price": 4500
    },

    "selected_hotel": {
        "hotel_id": "H002",
        "name": "Palm Paradise Hotel",
        "price_per_night": 2800
    },

    "selected_activities": [],

    # Itinerary
    "itinerary": None,

    # HITL
    "requires_approval": True,
    "approval_status": None,

    "pending_action": {
        "action": "BOOK_TRIP",
        "message": (
            "The agent wants to book the selected "
            "flight and hotel. Human approval is "
            "required before booking."
        ),
        "tool_name": "book_trip",
        "tool_args": {
            "flight_id": "F001",
            "hotel_id": "H002",
            "passengers": 2,
            "destination": "Goa"
        },
        "origin": "Delhi",
        "destination": "Goa",
        "start_date": "2026-11-10",
        "end_date": "2026-11-15",
        "passengers": 2
    },

    # Error / tracking
    "error": None,
    "step_count": 0
}


# ============================================================
# GRAPH CONFIGURATION
# ============================================================

config = {
    "configurable": {
        "thread_id": "travelmate-hitl-test"
    }
}


# ============================================================
# START TEST
# ============================================================

print("\n")
print("============================================================")
print("             TRAVELMATE AI - HITL TEST")
print("============================================================")
print("\nStarting HITL test...\n")


result = travelmate_graph.invoke(
    initial_state,
    config=config
)


# ============================================================
# CHECK FOR INTERRUPT
# ============================================================

if "__interrupt__" in result:

    print("\n")
    print("============================================================")
    print("             HUMAN APPROVAL REQUIRED")
    print("============================================================")

    interrupt_data = result["__interrupt__"]

    print("\nApproval request:")
    print(interrupt_data)

    print("\n============================================================")
    print("Enter your decision")
    print("1. APPROVE")
    print("2. REJECT")
    print("============================================================")

    user_input = input("\nYour choice: ").strip().lower()

    if user_input in (
        "1",
        "approve",
        "approved",
        "yes",
        "y"
    ):
        approval = {
            "approved": True
        }

    elif user_input in (
        "2",
        "reject",
        "rejected",
        "no",
        "n"
    ):
        approval = {
            "approved": False
        }

    else:
        print("\nInvalid choice.")
        print("Please run the test again.")
        raise SystemExit

    print("\nResuming TravelMate AI...\n")

    final_result = travelmate_graph.invoke(
        Command(
            resume=approval
        ),
        config=config
    )

else:

    print("\nWARNING:")
    print("No HITL interrupt was triggered.")

    final_result = result


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("============================================================")
print("                  FINAL RESULT")
print("============================================================")

print("\nDecision:")
print(final_result.get("decision_type"))

print("\nApproval Status:")
print(final_result.get("approval_status"))

print("\nExecuted Tools:")
print(final_result.get("executed_tools"))

print("\nSteps:")
print(final_result.get("step_count"))

print("\nError:")
print(final_result.get("error"))

print("\nTool Result:")
print(final_result.get("tool_result"))

print("\nDecision Content:")
print(final_result.get("decision_content"))

print("\n============================================================")
print("                    TEST COMPLETE")
print("============================================================\n")