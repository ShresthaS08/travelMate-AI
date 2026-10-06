import asyncio

from mcp import Client, StdioServerParameters


async def main():

    server = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"]
    )

    async with Client(server) as client:

        # ==========================================
        # STEP 1: DISCOVER TOOLS
        # ==========================================

        result = await client.list_tools()

        print("\n========== DISCOVERED MCP TOOLS ==========\n")

        for tool in result.tools:
            print("Tool name:", tool.name)
            print("Description:", tool.description)
            print("Input schema:")
            print(tool.input_schema)
            print("\n" + "=" * 60)


        # ==========================================
        # STEP 2: EXECUTE search_flights
        # ==========================================

        print("\n========== EXECUTING search_flights ==========\n")

        flight_result = await client.call_tool(
            "search_flights",
            {
                "origin": "Delhi",
                "destination": "Goa",
                "date": "2026-11-10",
                "passengers": 2
            }
        )

        print(flight_result)


        # ==========================================
        # STEP 3: EXECUTE search_hotels
        # ==========================================

        print("\n========== EXECUTING search_hotels ==========\n")

        hotel_result = await client.call_tool(
            "search_hotels",
            {
                "destination": "Goa",
                "check_in": "2026-11-10",
                "check_out": "2026-11-15",
                "guests": 2
            }
        )

        print(hotel_result)


        # ==========================================
        # STEP 4: EXECUTE search_activities
        # ==========================================

        print("\n========== EXECUTING search_activities ==========\n")

        activity_result = await client.call_tool(
            "search_activities",
            {
                "destination": "Goa",
                "preferences": [
                    "beaches",
                    "good food"
                ]
            }
        )

        print(activity_result)


        # ==========================================
        # STEP 5: EXECUTE calculate_budget
        # ==========================================

        print("\n========== EXECUTING calculate_budget ==========\n")

        budget_result = await client.call_tool(
            "calculate_budget",
            {
                "flight_cost": 9000,
                "hotel_cost": 14000,
                "activity_cost": 2500,
                "food_cost": 6000,
                "transport_cost": 3000,
                "budget": 50000
            }
        )

        print(budget_result)


if __name__ == "__main__":
    asyncio.run(main())