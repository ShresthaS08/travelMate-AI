from langgraph.types import interrupt

from app.state import AgentState


def human_approval_node(state: AgentState) -> dict:
    """
    Pause execution and request human approval
    before executing a sensitive action.
    """

    pending_action = state.get("pending_action")

    if not pending_action:
        return {
            "requires_approval": False,
            "approval_status": "not_required",
            "error": None,
            "step_count": state["step_count"] + 1
        }

    print("\n========== HUMAN APPROVAL REQUIRED ==========\n")

    print(
        "Action:",
        pending_action.get("action")
    )

    print(
        "Message:",
        pending_action.get("message")
    )

    print(
        "\nTool:",
        pending_action.get("tool_name")
    )

    print(
        "Arguments:",
        pending_action.get("tool_args")
    )

    print(
        "\n=============================================\n"
    )

    # --------------------------------------------------------
    # PAUSE GRAPH AND WAIT FOR HUMAN DECISION
    # --------------------------------------------------------

    approval = interrupt({
        "type": "human_approval",
        "action": pending_action.get("action"),
        "message": pending_action.get("message"),
        "tool_name": pending_action.get("tool_name"),
        "tool_args": pending_action.get("tool_args"),
        "details": pending_action
    })

    # --------------------------------------------------------
    # PROCESS HUMAN RESPONSE
    # --------------------------------------------------------

    if isinstance(approval, dict):
        approved = approval.get("approved", False)
    else:
        approved = bool(approval)

    if approved:

        approval_status = "approved"

        print(
            "\nHuman approval received."
        )

    else:

        approval_status = "rejected"

        print(
            "\nHuman approval rejected."
        )

    print(
        "Approval status:",
        approval_status
    )

    print(
        "=============================================\n"
    )

    return {
        "requires_approval": False,
        "approval_status": approval_status,
        "error": None,
        "step_count": state["step_count"] + 1
    }