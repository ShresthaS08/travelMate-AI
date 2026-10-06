from dotenv import load_dotenv

from langfuse import (
    get_client,
    propagate_attributes,
)

from langfuse.langchain import CallbackHandler

from app.graph import travelmate_graph


load_dotenv()


# =========================================================
# LANGFUSE
# =========================================================

langfuse = get_client()

handler = CallbackHandler()


# =========================================================
# TEST STATE
# =========================================================

initial_state = {
    "messages": [],

    "origin": "Delhi",
    "destination": "Goa",
    "start_date": "2026-11-10",
    "end_date": "2026-11-15",
    "passengers": 2,
    "budget": 50000,
    "preferences": [
        "beach",
        "food",
    ],
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


# =========================================================
# RUN
# =========================================================

config = {
    "configurable": {
        "thread_id": "langfuse-full-test-001",
    },

    "callbacks": [
        handler,
    ],

    "run_name": "travelmate-full-execution",
}


print("\n================================================")
print("       TRAVELMATE LANGFUSE FULL TRACE TEST")
print("================================================")


with propagate_attributes(
    trace_name="TravelMate AI - Full Execution",
    metadata={
        "application": "TravelMate-AI",
        "framework": "LangGraph",
        "test": "full-telemetry",
    },
    tags=[
        "travelmate",
        "langgraph",
        "full-trace",
    ],
):

    result = travelmate_graph.invoke(
        initial_state,
        config,
    )


print("\nGraph execution completed.")

print(
    "\nFinal destination:",
    result.get("destination"),
)

print(
    "Executed tools:",
    result.get("executed_tools"),
)

print(
    "Step count:",
    result.get("step_count"),
)

print(
    "Error:",
    result.get("error"),
)


# =========================================================
# FLUSH
# =========================================================

langfuse.flush()


print("\nLangfuse trace flushed.")

print("\n================================================")
print("              TEST COMPLETE")
print("================================================")