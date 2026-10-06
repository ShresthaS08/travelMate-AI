from app.state import AgentState


# ============================================================
# PRE-EXECUTION HOOK
# ============================================================

def pre_execution_hook(state: AgentState) -> AgentState:
    """
    Runs before each agent execution cycle.

    Responsibilities:
    - Validate important state fields
    - Check step limit
    - Log the current execution state
    """

    print("\n========== PRE-EXECUTION HOOK ==========\n")

    # --------------------------------------------------------
    # Validate step count
    # --------------------------------------------------------

    if state["step_count"] < 0:
        raise ValueError(
            "step_count cannot be negative."
        )

    # --------------------------------------------------------
    # Validate passengers
    # --------------------------------------------------------

    if state["passengers"] <= 0:
        raise ValueError(
            "Passengers must be greater than 0."
        )

    # --------------------------------------------------------
    # Validate budget
    # --------------------------------------------------------

    if state["budget"] is not None and state["budget"] < 0:
        raise ValueError(
            "Budget cannot be negative."
        )

    # --------------------------------------------------------
    # Log execution information
    # --------------------------------------------------------

    print("Current step:", state["step_count"])
    print("Origin:", state["origin"])
    print("Destination:", state["destination"])
    print("Passengers:", state["passengers"])
    print("Budget:", state["budget"])
    print("Executed tools:", state.get("executed_tools", []))

    print("\nPre-execution validation passed.")
    print("========================================\n")

    return state


# ============================================================
# POST-EXECUTION HOOK
# ============================================================

def post_execution_hook(
    state: AgentState
) -> AgentState:
    """
    Runs after an agent execution cycle.

    Responsibilities:
    - Log the result
    - Check for errors
    - Display execution information
    """

    print("\n========== POST-EXECUTION HOOK ==========\n")

    # --------------------------------------------------------
    # Check for errors
    # --------------------------------------------------------

    if state.get("error"):

        print("Execution completed with an error:")
        print(state["error"])

    else:

        print("Execution completed successfully.")

    # --------------------------------------------------------
    # Display execution information
    # --------------------------------------------------------

    print("Current step:", state["step_count"])
    print(
        "Decision type:",
        state.get("decision_type")
    )
    print(
        "Tool:",
        state.get("tool_name")
    )
    print(
        "Executed tools:",
        state.get("executed_tools", [])
    )

    print("\n=========================================\n")

    return state