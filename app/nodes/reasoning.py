import os
import time
import asyncio
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.state import AgentState
from app.mcp_client import discover_mcp_tools


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LLM CONFIGURATION
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0
)


# ============================================================
# DYNAMIC MCP TOOL DISCOVERY
# ============================================================

def get_mcp_tools_description() -> str:
    """
    Discover available tools from the MCP server and
    convert their metadata into a prompt-friendly format.
    """

    tools = asyncio.run(
        discover_mcp_tools()
    )

    if not tools:
        return "No MCP tools are currently available."

    tools_description = ""

    for index, tool in enumerate(
        tools,
        start=1
    ):
        tools_description += f"""
{index}. {tool["name"]}

Description:

{tool["description"]}

Input schema:

{json.dumps(tool["input_schema"], indent=2)}

"""

    return tools_description


# ============================================================
# NORMALIZE GEMINI RESPONSE
# ============================================================

def normalize_gemini_response(content) -> str:
    """
    Normalize Gemini response content into a plain string.

    Gemini models may return either:

        "plain text response"

    or structured content such as:

        [
            {
                "type": "text",
                "text": "DECISION: TOOL_REQUEST..."
            }
        ]

    The reasoning parser expects a string, so both formats
    are converted into one consistent string representation.
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            # Structured Gemini content block
            if isinstance(item, dict):

                text = item.get("text")

                if text:
                    text_parts.append(
                        str(text)
                    )

            # String content block
            elif isinstance(item, str):

                text_parts.append(item)

            # Object with a "text" attribute
            elif hasattr(item, "text"):

                text = getattr(
                    item,
                    "text",
                    None
                )

                if text:
                    text_parts.append(
                        str(text)
                    )

        return "\n".join(text_parts)

    # Fallback for unexpected response formats
    return str(content)


# ============================================================
# REASONING NODE
# ============================================================

def reasoning_node(state: AgentState) -> dict:

    print("\n========== REASONING NODE ==========\n")

    # --------------------------------------------------------
    # Dynamically discover MCP tools
    # --------------------------------------------------------

    try:

        tools_description = get_mcp_tools_description()

        print("Discovered MCP tools:")
        print(tools_description)

    except Exception as e:

        error_message = (
            f"MCP tool discovery failed: {str(e)}"
        )

        print(error_message)

        return {
            "decision_type": "ERROR",
            "decision_content": error_message,
            "error": error_message,
            "step_count": state["step_count"] + 1
        }

    # --------------------------------------------------------
    # Current state information
    # --------------------------------------------------------

    origin = state.get("origin")
    destination = state.get("destination")
    start_date = state.get("start_date")
    end_date = state.get("end_date")
    passengers = state.get("passengers")
    budget = state.get("budget")
    preferences = state.get("preferences", [])

    # Whether the user explicitly wants the trip booked
    booking_requested = state.get(
        "booking_requested",
        False
    )

    executed_tools = state.get(
        "executed_tools",
        []
    )

    # Latest tool result
    tool_result = state.get(
        "tool_result"
    )

    # All previously executed tool results
    tool_results = state.get(
        "tool_results",
        {}
    )

    error = state.get(
        "error"
    )

    approval_status = state.get(
        "approval_status"
    )

    # --------------------------------------------------------
    # Build reasoning prompt
    # --------------------------------------------------------

    prompt = f"""
You are the reasoning engine for TravelMate AI,
an intelligent travel planning and booking agent.

Your job is to analyze the user's travel requirements,
decide what action should happen next, and select an
appropriate MCP tool when necessary.

============================================================
AVAILABLE MCP TOOLS
============================================================

The following tools were dynamically discovered from
the MCP server:

{tools_description}

IMPORTANT:

- Only use tools listed above.
- Do not invent tool names.
- Use the exact tool name.
- Arguments must match the tool's input schema.

============================================================
TRAVEL REQUIREMENTS
============================================================

Origin:

{origin}

Destination:

{destination}

Start Date:

{start_date}

End Date:

{end_date}

Passengers:

{passengers}

Budget:

{budget}

Preferences:

{preferences}

============================================================
BOOKING REQUEST
============================================================

Booking Requested:

{booking_requested}

============================================================
PREVIOUSLY EXECUTED TOOLS
============================================================

{executed_tools}

============================================================
LAST TOOL RESULT
============================================================

{tool_result}

============================================================
ALL PREVIOUS TOOL RESULTS
============================================================

{json.dumps(tool_results, indent=2)}

============================================================
PREVIOUS ERROR
============================================================

{error}

============================================================
APPROVAL STATUS
============================================================

{approval_status}

============================================================
DECISION RULES
============================================================

1. Analyze the current travel requirements.

2. If information is needed from an available MCP tool,
   request that tool.

3. Do not request a tool that has already been successfully
   executed unless its result is clearly insufficient.

4. Use the results of previously executed tools when making
   the next decision.

5. If booking_requested is true, do not stop at a travel
   recommendation.

6. If booking_requested is true and the required flight and
   hotel search results are available, request the
   book_trip tool using valid IDs from those results.

7. If booking_requested is false, provide a final travel
   recommendation once enough information has been collected.

8. Do not invent flight, hotel, activity, or budget data.

9. If a tool is required, use exactly the tool name and
   argument structure provided by the MCP server.

10. The application will independently enforce human approval
    before executing the book_trip tool.

============================================================
RESPONSE FORMAT
============================================================

If you need to execute an MCP tool, respond EXACTLY like this:

DECISION: TOOL_REQUEST
TOOL: <tool name>
ARGUMENTS: <valid JSON object>

Example:

DECISION: TOOL_REQUEST
TOOL: search_flights
ARGUMENTS: {{"origin": "Delhi", "destination": "Goa", "date": "2026-11-10", "passengers": 2}}

If you have enough information to answer the user, respond:

DECISION: FINAL_RESPONSE
CONTENT: <your complete response to the user>

Do not include any additional decision format.
"""

    # --------------------------------------------------------
    # Prepare messages for Gemini
    # --------------------------------------------------------

    prompt_messages = [
        (
            "system",
            """
You are TravelMate AI's reasoning engine.

Follow the requested response format exactly.

Never invent MCP tools.

Never invent tool arguments.

If booking is required, request the book_trip tool.

The application will handle human approval before
that tool is executed.
"""
        ),
        (
            "human",
            prompt
        )
    ]

    # --------------------------------------------------------
    # Call Gemini with retry handling
    # --------------------------------------------------------

    max_retries = 3
    response = None

    for attempt in range(max_retries):

        try:

            print(
                f"\nCalling Gemini "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            response = llm.invoke(
                prompt_messages
            )

            break

        except Exception as e:

            print(
                f"\nGemini request failed "
                f"(attempt {attempt + 1}/{max_retries})"
            )

            print("Error:", e)

            if attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

            else:

                print(
                    "\nGemini failed after all retry attempts."
                )

                return {
                    "decision_type": "ERROR",
                    "decision_content": str(e),
                    "error": str(e),
                    "step_count": state["step_count"] + 1
                }

    # --------------------------------------------------------
    # Extract and normalize Gemini response
    # --------------------------------------------------------

    raw_content = response.content

    raw_response = normalize_gemini_response(
        raw_content
    )

    print(
        "\n========== RAW GEMINI RESPONSE ==========\n"
    )

    print(raw_response)

    print(
        "\n==========================================\n"
    )

    # --------------------------------------------------------
    # Parse decision
    # --------------------------------------------------------

    decision_type = None
    decision_content = None
    tool_name = None
    tool_args = {}

    # IMPORTANT:
    # raw_response is now always a string.
    lines = raw_response.splitlines()

    for line in lines:

        line = line.strip()

        if line.startswith("DECISION:"):

            decision_type = line.split(
                ":",
                1
            )[1].strip()

        elif line.startswith("TOOL:"):

            tool_name = line.split(
                ":",
                1
            )[1].strip()

        elif line.startswith("ARGUMENTS:"):

            arguments_text = line.split(
                ":",
                1
            )[1].strip()

            try:

                tool_args = json.loads(
                    arguments_text
                )

            except json.JSONDecodeError:

                print(
                    "\nWARNING: Could not parse tool arguments."
                )

                print(
                    "Arguments received:",
                    arguments_text
                )

                tool_args = {}

        elif line.startswith("CONTENT:"):

            decision_content = line.split(
                ":",
                1
            )[1].strip()

    # --------------------------------------------------------
    # Handle multi-line FINAL_RESPONSE content
    # --------------------------------------------------------

    if decision_type == "FINAL_RESPONSE":

        content_lines = []

        capture = False

        for line in lines:

            if line.startswith("CONTENT:"):

                capture = True

                content_lines.append(
                    line.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif capture:

                content_lines.append(
                    line
                )

        decision_content = "\n".join(
            content_lines
        ).strip()

    # --------------------------------------------------------
    # Validate decision
    # --------------------------------------------------------

    if decision_type is None:

        error_message = (
            "Gemini response did not contain a valid "
            "DECISION field."
        )

        print(
            "\nWARNING:",
            error_message
        )

        return {
            "decision_type": "ERROR",
            "decision_content": error_message,
            "error": error_message,
            "step_count": state["step_count"] + 1
        }

    # --------------------------------------------------------
    # Validate tool request
    # --------------------------------------------------------

    if decision_type == "TOOL_REQUEST":

        if not tool_name:

            error_message = (
                "LLM requested a tool but did not provide "
                "a tool name."
            )

            return {
                "decision_type": "ERROR",
                "decision_content": error_message,
                "error": error_message,
                "step_count": state["step_count"] + 1
            }

        if not isinstance(tool_args, dict):

            error_message = (
                "Tool arguments must be a JSON object."
            )

            return {
                "decision_type": "ERROR",
                "decision_content": error_message,
                "error": error_message,
                "step_count": state["step_count"] + 1
            }

        # ----------------------------------------------------
        # HITL SECURITY BOUNDARY
        # ----------------------------------------------------
        # book_trip is a side-effecting operation.
        # Never allow it to execute without human approval.
        # ----------------------------------------------------

        if tool_name == "book_trip":

            pending_action = {
                "action": "BOOK_TRIP",
                "message": (
                    "The agent wants to book the selected "
                    "flight and hotel. Human approval is "
                    "required before booking."
                ),
                "tool_name": tool_name,
                "tool_args": tool_args,
                "origin": origin,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "passengers": passengers
            }

            print(
                "\n========== HITL ROUTING ==========\n"
            )

            print(
                "Booking request detected."
            )

            print(
                "Human approval is required "
                "before book_trip can execute."
            )

            print(
                "\n===================================\n"
            )

            return {
                "decision_type": "APPROVAL_REQUIRED",
                "decision_content": (
                    "Human approval is required "
                    "before booking the trip."
                ),
                "tool_name": tool_name,
                "tool_args": tool_args,
                "requires_approval": True,
                "pending_action": pending_action,
                "approval_status": None,
                "error": None,
                "step_count": state["step_count"] + 1
            }

    # --------------------------------------------------------
    # Return updated state
    # --------------------------------------------------------

    print(
        "========== PARSED DECISION ==========\n"
    )

    print(
        "Decision:",
        decision_type
    )

    print(
        "Tool:",
        tool_name
    )

    print(
        "Arguments:",
        tool_args
    )

    print(
        "Content:",
        decision_content
    )

    print(
        "\n=====================================\n"
    )

    return {
        "decision_type": decision_type,
        "decision_content": decision_content,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "error": None,
        "step_count": state["step_count"] + 1
    }