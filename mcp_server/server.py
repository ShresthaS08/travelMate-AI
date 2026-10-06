from mcp.server import MCPServer


mcp = MCPServer("TravelMate MCP Server")


@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    date: str,
    passengers: int
) -> dict:
    """Search available flights between two cities."""

    return {
        "status": "success",
        "origin": origin,
        "destination": destination,
        "date": date,
        "passengers": passengers,
        "flights": [
            {
                "flight_id": "F001",
                "airline": "IndiGo",
                "departure": "08:00",
                "arrival": "10:30",
                "price": 4500
            },
            {
                "flight_id": "F002",
                "airline": "Air India",
                "departure": "14:00",
                "arrival": "16:30",
                "price": 5200
            }
        ]
    }


@mcp.tool()
def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int
) -> dict:
    """Search available hotels at the destination."""

    return {
        "status": "success",
        "destination": destination,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "hotels": [
            {
                "hotel_id": "H001",
                "name": "Goa Beach Resort",
                "location": destination,
                "price_per_night": 3500,
                "rating": 4.5,
                "available_rooms": 5
            },
            {
                "hotel_id": "H002",
                "name": "Palm Paradise Hotel",
                "location": destination,
                "price_per_night": 2800,
                "rating": 4.2,
                "available_rooms": 8
            },
            {
                "hotel_id": "H003",
                "name": "Ocean View Resort",
                "location": destination,
                "price_per_night": 4200,
                "rating": 4.7,
                "available_rooms": 3
            }
        ]
    }


@mcp.tool()
def search_activities(
    destination: str,
    preferences: list[str]
) -> dict:
    """Search activities based on travel preferences."""

    return {
        "status": "success",
        "destination": destination,
        "preferences": preferences,
        "activities": [
            {
                "activity_id": "A001",
                "name": "Baga Beach",
                "category": "beaches",
                "price": 0
            },
            {
                "activity_id": "A002",
                "name": "Fort Aguada",
                "category": "sightseeing",
                "price": 100
            },
            {
                "activity_id": "A003",
                "name": "Dudhsagar Falls",
                "category": "nature",
                "price": 1200
            },
            {
                "activity_id": "A004",
                "name": "Scuba Diving",
                "category": "adventure",
                "price": 2500
            }
        ]
    }


@mcp.tool()
def calculate_budget(
    flight_cost: float,
    hotel_cost: float,
    activity_cost: float,
    food_cost: float,
    transport_cost: float,
    budget: float
) -> dict:
    """Calculate total trip cost and check whether it is within budget."""

    total = (
        flight_cost
        + hotel_cost
        + activity_cost
        + food_cost
        + transport_cost
    )

    remaining = budget - total

    return {
        "status": "success",
        "flight_cost": flight_cost,
        "hotel_cost": hotel_cost,
        "activity_cost": activity_cost,
        "food_cost": food_cost,
        "transport_cost": transport_cost,
        "total_cost": total,
        "budget": budget,
        "remaining_budget": remaining,
        "within_budget": total <= budget
    }


@mcp.tool()
def book_trip(
    flight_id: str,
    hotel_id: str,
    passengers: int,
    destination: str
) -> dict:
    """Book the selected flight and hotel for the trip."""

    return {
        "status": "success",
        "booking_id": "BK001",
        "flight_id": flight_id,
        "hotel_id": hotel_id,
        "passengers": passengers,
        "destination": destination,
        "message": "Trip booked successfully."
    }


if __name__ == "__main__":
    mcp.run()