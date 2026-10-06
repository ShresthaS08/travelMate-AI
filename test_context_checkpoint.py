from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.state import AgentState
from app.nodes.context_manager import context_manager_node


# ============================================================
# TEST GRAPH
# ============================================================

graph = StateGraph(AgentState)

graph.add_node(
    "context_manager",
    context_manager_node
)

graph.set_entry_point("context_manager")

graph.add_edge(
    "context_manager",
    END
)


# ============================================================
# CHECKPOINTING
# ============================================================

checkpointer = InMemorySaver()

test_graph = graph.compile(
    checkpointer=checkpointer
)


# ============================================================
# INITIAL STATE
# ============================================================

initial_state = {

    "messages": [],

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

    "decision_type": None,
    "decision_content": None,

    "tool_name": None,
    "tool_args": {},

    "tool_result": None,

    "tool_results": {
        "search_flights": {
            "status": "success",
            "flights": [
                {
                    "flight_id": "F001",
                    "airline": "IndiGo",
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
                    "price_per_night": 2800
                }
            ]
        }
    },

    "executed_tools": [
        "search_flights",
        "search_hotels"
    ],

    "selected_flight": {
        "flight_id": "F001"
    },

    "selected_hotel": {
        "hotel_id": "H002"
    },

    "selected_activities": [],

    "itinerary": None,

    "requires_approval": False,

    "approval_status": None,

    "pending_action": None,

    "error": None,

    "step_count": 0
}


# ============================================================
# THREAD CONFIGURATION
# ============================================================

config = {
    "configurable": {
        "thread_id": "task7-context-test"
    }
}


# ============================================================
# RUN TEST
# ============================================================

print("\n")
print("=" * 60)
print("        TRAVELMATE AI - TASK 7 TEST")
print("=" * 60)

print("\nStarting context + checkpoint test...")


result = test_graph.invoke(
    initial_state,
    config
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("              TEST RESULT")
print("=" * 60)

print("\nDestination:")
print(result["destination"])

print("\nMessages retained:")
print(len(result["messages"]))

print("\nTool results retained:")
print(len(result["tool_results"]))

print("\nExecuted tools:")
print(result["executed_tools"])

print("\nStep count:")
print(result["step_count"])

print("\nError:")
print(result["error"])


# ============================================================
# CHECKPOINT VERIFICATION
# ============================================================

checkpoint = test_graph.get_state(config)


print("\n")
print("=" * 60)
print("          CHECKPOINT VERIFICATION")
print("=" * 60)

print("\nCheckpoint exists:")

if checkpoint and checkpoint.values:
    print("YES")

    print("\nCheckpointed destination:")
    print(checkpoint.values["destination"])

    print("\nCheckpointed step count:")
    print(checkpoint.values["step_count"])

    print("\nCheckpointed executed tools:")
    print(checkpoint.values["executed_tools"])

else:
    print("NO")


print("\n")
print("=" * 60)
print("              TEST COMPLETE")
print("=" * 60)