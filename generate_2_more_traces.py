import time

from app.graph import travelmate_graph


scenarios = [
    {
        "name": "Ahmedabad_to_Goa",
        "origin": "Ahmedabad",
        "destination": "Goa",
        "start_date": "2026-11-10",
        "end_date": "2026-11-15",
        "passengers": 2,
        "budget": 50000,
        "preferences": ["beaches", "relaxation"],
        "booking_requested": False,
    },
    {
        "name": "Jaipur_to_Mumbai",
        "origin": "Jaipur",
        "destination": "Mumbai",
        "start_date": "2026-12-05",
        "end_date": "2026-12-10",
        "passengers": 2,
        "budget": 60000,
        "preferences": ["food", "sightseeing"],
        "booking_requested": False,
    },
]


print("=" * 65)
print("       GENERATING 2 ADDITIONAL EVALUATION TRACES")
print("=" * 65)


successful = 0
failed = 0


for index, scenario in enumerate(scenarios, start=1):

    print(f"\n[{index}/2] {scenario['origin']} -> {scenario['destination']}")

    thread_id = (
        f"evaluation-extra-{scenario['name']}-"
        f"{int(time.time())}-{index}"
    )

    initial_state = {
        "messages": [],
        "origin": scenario["origin"],
        "destination": scenario["destination"],
        "start_date": scenario["start_date"],
        "end_date": scenario["end_date"],
        "passengers": scenario["passengers"],
        "budget": scenario["budget"],
        "preferences": scenario["preferences"],
        "booking_requested": scenario["booking_requested"],
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

    try:
        result = travelmate_graph.invoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            },
        )

        print("SUCCESS")
        print("Final decision:", result.get("decision_type"))
        successful += 1

    except Exception as e:
        print("FAILED")
        print("Error:", e)
        failed += 1


print("\n" + "=" * 65)
print("             TRACE GENERATION COMPLETE")
print("=" * 65)

print(f"\nSuccessful executions: {successful}")
print(f"Failed executions: {failed}")

print("\nWe now have the additional traces required for evaluation.")