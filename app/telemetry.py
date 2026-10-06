import time

from dotenv import load_dotenv
from langfuse import (
    get_client,
    observe,
    propagate_attributes,
)

load_dotenv()


# =========================================================
# LANGFUSE CLIENT
# =========================================================

langfuse = get_client()


# =========================================================
# COMPLETE GRAPH TRACE
# =========================================================

@observe(
    name="travelmate-agent",
    as_type="agent",
)
def trace_agent_execution(
    input_data: dict,
    execution_function,
):
    """
    Creates one root Langfuse trace for a complete
    TravelMate execution.
    """

    with propagate_attributes(
        trace_name="TravelMate AI",
        metadata={
            "application": "TravelMate-AI",
            "framework": "LangGraph",
            "telemetry_version": "1.0",
        },
        tags=[
            "travelmate",
            "langgraph",
            "travel-agent",
        ],
    ):

        start_time = time.perf_counter()

        try:

            result = execution_function()

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            print(
                f"\nLangfuse graph trace completed "
                f"in {elapsed_ms:.2f} ms"
            )

            return result

        except Exception as exc:

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            print(
                f"\nLangfuse graph trace failed "
                f"after {elapsed_ms:.2f} ms"
            )

            print("Error:", str(exc))

            raise


# =========================================================
# GRAPH NODE TRACE
# =========================================================

def trace_graph_node(
    node_name: str,
    state: dict,
    execution_function,
):
    """
    Creates a Langfuse span for one LangGraph node.
    """

    start_time = time.perf_counter()

    with langfuse.start_as_current_observation(
        name=f"node:{node_name}",
        as_type="span",
        input={
            "node": node_name,
            "step_count": state.get(
                "step_count"
            ),
            "tool_name": state.get(
                "tool_name"
            ),
            "decision_type": state.get(
                "decision_type"
            ),
        },
    ) as observation:

        try:

            result = execution_function()

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            observation.update(
                output={
                    "node": node_name,
                    "step_count": result.get(
                        "step_count",
                        state.get("step_count"),
                    ),
                    "decision_type": result.get(
                        "decision_type"
                    ),
                    "tool_name": result.get(
                        "tool_name"
                    ),
                    "error": result.get(
                        "error"
                    ),
                    "latency_ms": round(
                        elapsed_ms,
                        2,
                    ),
                }
            )

            return result

        except Exception as exc:

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            observation.update(
                output={
                    "node": node_name,
                    "error": str(exc),
                    "latency_ms": round(
                        elapsed_ms,
                        2,
                    ),
                },
                level="ERROR",
                status_message=str(exc),
            )

            raise


# =========================================================
# TOOL TRACE
# =========================================================

def trace_tool_execution(
    tool_name: str,
    tool_args: dict,
    execution_function,
):
    """
    Traces an MCP/JSON-RPC tool execution.

    The input contains the JSON-RPC-style tool payload.
    The output contains the tool response.
    """

    start_time = time.perf_counter()

    with langfuse.start_as_current_observation(
        name=f"tool:{tool_name}",
        as_type="tool",
        input={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args,
            },
        },
    ) as observation:

        try:

            result = execution_function()

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            observation.update(
                output={
                    "jsonrpc": "2.0",
                    "result": result,
                    "latency_ms": round(
                        elapsed_ms,
                        2,
                    ),
                }
            )

            return result

        except Exception as exc:

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            observation.update(
                output={
                    "jsonrpc": "2.0",
                    "error": str(exc),
                    "latency_ms": round(
                        elapsed_ms,
                        2,
                    ),
                },
                level="ERROR",
                status_message=str(exc),
            )

            raise


# =========================================================
# LLM GENERATION TRACE
# =========================================================

def trace_llm_generation(
    model_name: str,
    prompt,
    execution_function,
):
    """
    Creates a Langfuse generation observation around
    an LLM call.

    Token usage is captured when the LLM response exposes
    usage_metadata.
    """

    with langfuse.start_as_current_observation(
        name="reasoning-llm",
        as_type="generation",
        model=model_name,
        input=prompt,
    ) as generation:

        start_time = time.perf_counter()

        try:

            response = execution_function()

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            usage = getattr(
                response,
                "usage_metadata",
                None,
            )

            output = getattr(
                response,
                "content",
                str(response),
            )

            update_data = {
                "output": output,
                "metadata": {
                    "latency_ms": round(
                        elapsed_ms,
                        2,
                    ),
                },
            }

            # ---------------------------------------------
            # Token usage
            # ---------------------------------------------

            if usage:

                input_tokens = usage.get(
                    "input_tokens"
                )

                output_tokens = usage.get(
                    "output_tokens"
                )

                total_tokens = usage.get(
                    "total_tokens"
                )

                usage_details = {}

                if input_tokens is not None:
                    usage_details[
                        "input"
                    ] = input_tokens

                if output_tokens is not None:
                    usage_details[
                        "output"
                    ] = output_tokens

                if total_tokens is not None:
                    usage_details[
                        "total"
                    ] = total_tokens

                if usage_details:
                    update_data[
                        "usage_details"
                    ] = usage_details

            generation.update(
                **update_data
            )

            return response

        except Exception as exc:

            generation.update(
                output={
                    "error": str(exc),
                    "latency_ms": round(
                        (
                            time.perf_counter()
                            - start_time
                        ) * 1000,
                        2,
                    ),
                },
                level="ERROR",
                status_message=str(exc),
            )

            raise


# =========================================================
# FLUSH
# =========================================================

def flush_langfuse():

    langfuse.flush()

    print(
        "\nLangfuse telemetry flushed."
    )