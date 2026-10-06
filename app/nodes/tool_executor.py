import asyncio

from app.state import AgentState
from app.mcp_client import call_mcp_tool
from app.telemetry import trace_tool_execution


def tool_executor_node(state: AgentState) -> dict:
    """
    Execute the requested MCP tool and record
    the execution in Langfuse telemetry.
    """

    tool_name = state["tool_name"]
    tool_args = state["tool_args"]

    # ========================================================
    # VALIDATE TOOL REQUEST
    # ========================================================

    if not tool_name:
        return {
            "tool_result": {
                "status": "error",
                "error": "No tool was requested."
            },
            "error": "No tool was requested.",
            "step_count": state["step_count"] + 1
        }

    # ========================================================
    # COPY EXISTING EXECUTION STATE
    # ========================================================

    executed_tools = state.get(
        "executed_tools",
        []
    ).copy()

    tool_results = state.get(
        "tool_results",
        {}
    ).copy()

    try:

        print(
            "\n========== MCP TOOL EXECUTION ==========\n"
        )

        print(
            "Tool:",
            tool_name
        )

        print(
            "Arguments:",
            tool_args
        )

        # ====================================================
        # MCP TOOL EXECUTION + LANGFUSE TELEMETRY
        # ====================================================

        result = trace_tool_execution(
            tool_name,
            tool_args,
            lambda: asyncio.run(
                call_mcp_tool(
                    tool_name,
                    tool_args
                )
            )
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        print(
            "\nMCP tool executed successfully."
        )

        print(
            "Result:",
            result
        )

        print(
            "========================================\n"
        )

        # Preserve all tool results
        tool_results[tool_name] = result

        # Avoid duplicate tool names
        if tool_name not in executed_tools:
            executed_tools.append(tool_name)

        return {
            "tool_result": result,
            "tool_results": tool_results,
            "error": None,
            "executed_tools": executed_tools,
            "step_count": state["step_count"] + 1
        }

    except Exception as e:

        error_message = str(e)

        print(
            "\n========== MCP TOOL ERROR ==========\n"
        )

        print(
            error_message
        )

        print(
            "====================================\n"
        )

        error_result = {
            "status": "error",
            "error": error_message
        }

        # Preserve the failed tool result
        tool_results[tool_name] = error_result

        return {
            "tool_result": error_result,
            "tool_results": tool_results,
            "error": error_message,
            "executed_tools": executed_tools,
            "step_count": state["step_count"] + 1
        }