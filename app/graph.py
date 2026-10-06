import sqlite3

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.state import AgentState

from app.nodes.reasoning import reasoning_node
from app.nodes.tool_executor import tool_executor_node
from app.nodes.human_approval import human_approval_node
from app.nodes.context_manager import context_manager_node

from app.hooks import (
    pre_execution_hook,
    post_execution_hook,
)


# =========================================================
# CONFIGURATION
# =========================================================

MAX_STEPS = 10


# =========================================================
# ROUTING: PRE-EXECUTION HOOK
# =========================================================

def route_after_pre_hook(state: AgentState):

    if state.get("error"):
        print("\nPre-hook detected an error.")
        return END

    return "context_manager"


# =========================================================
# ROUTING: REASONING NODE
# =========================================================

def route_after_reasoning(state: AgentState):

    # Safety limit
    if state["step_count"] >= MAX_STEPS:
        print(
            f"\nMaximum step limit of {MAX_STEPS} reached."
        )
        return "post_hook"

    # Human approval required
    if state.get("requires_approval"):
        print("\nRouting to HUMAN APPROVAL.")
        return "human_approval"

    # Tool request
    if state["decision_type"] == "TOOL_REQUEST":
        return "tool_executor"

    # Final response
    if state["decision_type"] == "FINAL_RESPONSE":
        return "post_hook"

    # Unknown decision type
    print(
        "\nWARNING: Unknown decision type:",
        state["decision_type"]
    )

    return "post_hook"


# =========================================================
# ROUTING: TOOL EXECUTOR
# =========================================================

def route_after_tool(state: AgentState):

    # Tool execution failed
    if state.get("error"):
        print("\nTool execution failed.")
        return "post_hook"

    # Safety limit
    if state["step_count"] >= MAX_STEPS:
        print(
            f"\nMaximum step limit of {MAX_STEPS} reached."
        )
        return "post_hook"

    # Tool requires human approval
    if state.get("requires_approval"):
        print(
            "\nTool execution requires HUMAN APPROVAL."
        )
        return "human_approval"

    # -----------------------------------------------------
    # BOOKING COMPLETED
    # -----------------------------------------------------
    #
    # book_trip is a side-effecting operation.
    # Once booking succeeds, do not send the result back
    # through the reasoning LLM again.
    #

    if state.get("tool_name") == "book_trip":
        print("\nBooking completed successfully.")
        return "post_hook"

    # Normal tools continue to reasoning
    return "reasoning"


# =========================================================
# ROUTING: HUMAN APPROVAL
# =========================================================

def route_after_human_approval(state: AgentState):

    approval_status = state.get(
        "approval_status"
    )

    # Approved
    if approval_status == "approved":
        print("\nHuman approved the action.")
        return "tool_executor"

    # Rejected
    if approval_status == "rejected":
        print("\nHuman rejected the action.")
        return "post_hook"

    # Unknown approval status
    print(
        "\nWARNING: Unknown approval status:",
        approval_status
    )

    return "post_hook"


# =========================================================
# ROUTING: POST HOOK
# =========================================================

def route_after_post_hook(state: AgentState):
    return END


# =========================================================
# CREATE STATE GRAPH
# =========================================================

graph = StateGraph(AgentState)


# =========================================================
# ADD NODES
# =========================================================

graph.add_node(
    "pre_hook",
    pre_execution_hook
)

graph.add_node(
    "context_manager",
    context_manager_node
)

graph.add_node(
    "reasoning",
    reasoning_node
)

graph.add_node(
    "tool_executor",
    tool_executor_node
)

graph.add_node(
    "human_approval",
    human_approval_node
)

graph.add_node(
    "post_hook",
    post_execution_hook
)


# =========================================================
# ENTRY POINT
# =========================================================

graph.set_entry_point(
    "pre_hook"
)


# =========================================================
# PRE-HOOK → CONTEXT MANAGER
# =========================================================

graph.add_conditional_edges(
    "pre_hook",
    route_after_pre_hook,
    {
        "context_manager": "context_manager",
        END: END,
    },
)


# =========================================================
# CONTEXT MANAGER → REASONING
# =========================================================

graph.add_edge(
    "context_manager",
    "reasoning"
)


# =========================================================
# REASONING ROUTING
# =========================================================

graph.add_conditional_edges(
    "reasoning",
    route_after_reasoning,
    {
        "tool_executor": "tool_executor",
        "human_approval": "human_approval",
        "post_hook": "post_hook",
    },
)


# =========================================================
# TOOL EXECUTOR ROUTING
# =========================================================

graph.add_conditional_edges(
    "tool_executor",
    route_after_tool,
    {
        "reasoning": "reasoning",
        "human_approval": "human_approval",
        "post_hook": "post_hook",
    },
)


# =========================================================
# HUMAN APPROVAL ROUTING
# =========================================================

graph.add_conditional_edges(
    "human_approval",
    route_after_human_approval,
    {
        "tool_executor": "tool_executor",
        "post_hook": "post_hook",
    },
)


# =========================================================
# POST-HOOK → END
# =========================================================

graph.add_conditional_edges(
    "post_hook",
    route_after_post_hook,
    {
        END: END,
    },
)


# =========================================================
# PERSISTENT SQLITE CHECKPOINTING
# =========================================================
#
# IMPORTANT:
# Do NOT use:
#
#     SqliteSaver.from_conn_string(...)
#
# in this version.
#
# That returns a context manager in the installed package
# version, which caused the "_GeneratorContextManager"
# error during graph.compile().
#
# Instead, create the SQLite connection directly and pass
# the actual connection to SqliteSaver.
#


sqlite_connection = sqlite3.connect(
    "travelmate_checkpoints.db",
    check_same_thread=False,
)


checkpointer = SqliteSaver(
    sqlite_connection
)


# Create the LangGraph checkpoint tables.
checkpointer.setup()


# =========================================================
# COMPILE GRAPH
# =========================================================

travelmate_graph = graph.compile(
    checkpointer=checkpointer
)