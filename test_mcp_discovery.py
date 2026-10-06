import asyncio

from app.mcp_client import discover_mcp_tools


async def main():

    tools = await discover_mcp_tools()

    print("\n========== DYNAMIC MCP TOOL DISCOVERY ==========\n")

    for tool in tools:

        print("Tool:", tool["name"])
        print("Description:", tool["description"])

        print("Input schema:")
        print(tool["input_schema"])

        print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())