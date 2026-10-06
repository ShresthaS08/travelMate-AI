from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.nodes.context_manager import context_manager_node


# ---------------------------------------------------------
# Create test messages
# ---------------------------------------------------------

messages = []

for i in range(12):

    if i % 2 == 0:
        messages.append(
            HumanMessage(
                content=f"User message {i + 1}: "
                f"I want to plan a trip to Goa."
            )
        )
    else:
        messages.append(
            AIMessage(
                content=f"Assistant message {i + 1}: "
                f"I can help plan your Goa trip."
            )
        )


# ---------------------------------------------------------
# Initial state
# ---------------------------------------------------------

initial_state = {
    "messages": messages,

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


# ---------------------------------------------------------
# Build a tiny LangGraph only for this test
# ---------------------------------------------------------

test_graph = StateGraph(AgentState)

test_graph.add_node(
    "context_manager",
    context_manager_node
)

test_graph.set_entry_point("context_manager")

test_graph.add_edge(
    "context_manager",
    END
)

compiled_graph = test_graph.compile()


# ---------------------------------------------------------
# Run test
# ---------------------------------------------------------

print("\n================================================")
print("       CONTEXT COMPACTION TEST")
print("================================================")

print("\nMessages BEFORE:")
print(len(initial_state["messages"]))


result = compiled_graph.invoke(initial_state)


# ---------------------------------------------------------
# Display result
# ---------------------------------------------------------

final_messages = result["messages"]

print("\nMessages AFTER LangGraph:")
print(len(final_messages))

print("\nFinal messages:")

for i, message in enumerate(
    final_messages,
    start=1
):

    print(
        f"{i}. "
        f"{type(message).__name__}: "
        f"{message.content[:200]}"
    )


print("\nStep count:")
print(result["step_count"])


print("\n================================================")
print("              TEST COMPLETE")
print("================================================")