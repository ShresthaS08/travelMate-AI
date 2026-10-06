import time

from dotenv import load_dotenv

from app.graph import travelmate_graph


load_dotenv()


# ============================================================
# EVALUATION SCENARIOS
# ============================================================

SCENARIOS = [
    {
        "name": "delhi_goa",
        "origin": "Delhi",
        "destination": "Goa",
        "start_date": "2026-11-10",
        "end_date": "2026-11-14",
        "passengers": 2,
        "budget": 50000,
        "preferences": ["beaches", "food"],
    },
    {
        "name": "mumbai_delhi",
        "origin": "Mumbai",
        "destination": "Delhi",
        "start_date": "2026-11-12",
        "end_date": "2026-11-15",
        "passengers": 1,
        "budget": 30000,
        "preferences": ["culture", "history"],
    },
    {
        "name": "bangalore_goa",
        "origin": "Bangalore",
        "destination": "Goa",
        "start_date": "2026-11-15",
        "end_date": "2026-11-18",
        "passengers": 2,
        "budget": 40000,
        "preferences": ["beaches", "nightlife"],
    },
    {
        "name": "pune_jaipur",
        "origin": "Pune",
        "destination": "Jaipur",
        "start_date": "2026-11-18",
        "end_date": "2026-11-21",
        "passengers": 2,
        "budget": 35000,
        "preferences": ["forts", "culture"],
    },
    {
        "name": "delhi_mumbai",
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-11-20",
        "end_date": "2026-11-23",
        "passengers": 2,
        "budget": 45000,
        "preferences": ["food", "shopping"],
    },
    {
        "name": "chennai_delhi",
        "origin": "Chennai",
        "destination": "Delhi",
        "start_date": "2026-11-22",
        "end_date": "2026-11-25",
        "passengers": 1,
        "budget": 30000,
        "preferences": ["history", "food"],
    },
    {
        "name": "hyderabad_goa",
        "origin": "Hyderabad",
        "destination": "Goa",
        "start_date": "2026-11-25",
        "end_date": "2026-11-29",
        "passengers": 3,
        "budget": 60000,
        "preferences": ["beaches", "adventure"],
    },
    {
        "name": "kolkata_jaipur",
        "origin": "Kolkata",
        "destination": "Jaipur",
        "start_date": "2026-11-28",
        "end_date": "2026-12-02",
        "passengers": 2,
        "budget": 50000,
        "preferences": ["culture", "photography"],
    },
]


# ============================================================
# INITIAL STATE
# ============================================================

def create_initial_state(scenario):

    return {
        "messages": [],

        "origin": scenario["origin"],
        "destination": scenario["destination"],
        "start_date": scenario["start_date"],
        "end_date": scenario["end_date"],
        "passengers": scenario["passengers"],
        "budget": scenario["budget"],
        "preferences": scenario["preferences"],

        "booking_requested": False,

        "decision_type": None,
        "decision_content": None,

        "tool_name": None,
        "tool_args": {},

        "tool_result": None,
        "tool_results": {},

        "executed_tools": [],

        "selected_flight": None,
        "selected_hotel": None,
        "selected_activities": [],

        "itinerary": None,

        "requires_approval": False,
        "approval_status": None,
        "pending_action": None,

        "error": None,

        "step_count": 0,
    }


# ============================================================
# RUN ONE SCENARIO
# ============================================================

def run_scenario(index, scenario):

    print("\n")
    print("=" * 65)
    print(f" EVALUATION TRACE {index}/8")
    print("=" * 65)

    print("Scenario:", scenario["name"])
    print(
        f"Route: {scenario['origin']} -> "
        f"{scenario['destination']}"
    )

    initial_state = create_initial_state(scenario)

    # IMPORTANT:
    # Every evaluation run gets a unique thread ID.
    # This allows LangGraph/Langfuse to record separate executions.

    thread_id = (
        f"evaluation-{scenario['name']}-"
        f"{int(time.time())}-{index}"
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        },
        "run_name": (
            f"TravelMate Evaluation - "
            f"{scenario['name']}"
        ),
        "metadata": {
            "evaluation": True,
            "evaluation_batch": "task-9a",
            "scenario": scenario["name"],
        },
        "tags": [
            "travelmate",
            "evaluation",
            "task-9a",
        ],
    }

    print("Thread ID:", thread_id)
    print("\nStarting graph execution...")

    try:

        result = travelmate_graph.invoke(
            initial_state,
            config
        )

        print("\nExecution completed.")

        print(
            "Final decision:",
            result.get("decision_type")
        )

        print(
            "Executed tools:",
            result.get("executed_tools", [])
        )

        print(
            "Error:",
            result.get("error")
        )

        return True

    except Exception as exc:

        print("\nExecution failed.")

        print(
            "Error:",
            str(exc)
        )

        # We still consider this a recorded evaluation
        # execution because Langfuse can capture failures.

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 65)
    print("       TRAVELMATE AI - EVALUATION TRACE GENERATOR")
    print("=" * 65)

    print("\nGenerating 8 additional TravelMate executions.")
    print("Each execution receives a unique thread ID.")
    print("\n")

    successful = 0
    failed = 0

    for index, scenario in enumerate(
        SCENARIOS,
        start=1
    ):

        success = run_scenario(
            index,
            scenario
        )

        if success:
            successful += 1
        else:
            failed += 1

        # Small delay between executions.
        if index < len(SCENARIOS):
            print("\nWaiting briefly before next execution...")
            time.sleep(2)

    print("\n")
    print("=" * 65)
    print("          TRACE GENERATION COMPLETE")
    print("=" * 65)

    print("\nSuccessful executions:", successful)
    print("Failed executions:", failed)

    print("\nNext step:")
    print("Open Langfuse and verify that the number of")
    print("unique TravelMate traces has increased.")
    print("=" * 65)


if __name__ == "__main__":
    main()