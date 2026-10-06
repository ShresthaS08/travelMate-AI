from langgraph.types import Command

from app.graph import travelmate_graph


# ============================================================
# INITIAL STATE
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
    "decision_type": None,
    "decision_content": None,

    # Tool execution
    "tool_name": None,
    "tool_args": {},
    "tool_result": None,
    "tool_results": {},
    "executed_tools": [],

    # Booking
    "selected_flight": None,
    "selected_hotel": None,
    "selected_activities": [],

    # Itinerary
    "itinerary": None,

    # Human approval
    "requires_approval": False,
    "approval_status": None,
    "pending_action": None,

    # Error handling
    "error": None,

    # Execution tracking
    "step_count": 0
}


# ============================================================
# THREAD CONFIGURATION
# ============================================================

config = {
    "configurable": {
        "thread_id": "travelmate-task6-demo"
    }
}


# ============================================================
# START GRAPH
# ============================================================

print("\n")
print("============================================================")
print("             TRAVELMATE AI - TASK 6 HITL")
print("============================================================")
print("\nStarting TravelMate AI...\n")


result = travelmate_graph.invoke(
    initial_state,
    config=config
)


# ============================================================
# CHECK WHETHER GRAPH WAS INTERRUPTED
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


    # --------------------------------------------------------
    # Convert user input to approval decision
    # --------------------------------------------------------

    if user_input in ("1", "approve", "approved", "yes", "y"):

        approval = {
            "approved": True
        }

    elif user_input in ("2", "reject", "rejected", "no", "n"):

        approval = {
            "approved": False
        }

    else:

        print("\nInvalid choice.")
        print("Please run the test again.")

        raise SystemExit


    # ========================================================
    # RESUME GRAPH
    # ========================================================

    print("\nResuming TravelMate AI...\n")


    final_result = travelmate_graph.invoke(
        Command(
            resume=approval
        ),
        config=config
    )


else:

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

print("\nDecision Content:")
print(final_result.get("decision_content"))

print("\n============================================================")
print("                    TEST COMPLETE")
print("============================================================\n")