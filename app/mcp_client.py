import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=["mcp_server/server.py"],
)


async def discover_mcp_tools():
    """
    Discover available tools from the local MCP server.
    """

    async with stdio_client(SERVER_PARAMS) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.list_tools()

            tools = []

            for tool in result.tools:

                tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                )

            return tools


async def call_mcp_tool(
    tool_name: str,
    tool_args: dict,
):
    """
    Execute an MCP tool through the local stdio MCP server.
    """

    async with stdio_client(SERVER_PARAMS) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=tool_args,
            )

            if result.isError:
                raise RuntimeError(
                    f"MCP tool '{tool_name}' returned an error."
                )

            if result.content:

                first_content = result.content[0]

                if hasattr(first_content, "text"):

                    try:
                        return json.loads(
                            first_content.text
                        )

                    except json.JSONDecodeError:

                        return {
                            "status": "success",
                            "result": first_content.text,
                        }

            # MCP can also provide structured content.
            if hasattr(result, "structuredContent"):

                structured = result.structuredContent

                if structured:
                    return structured

            return {}