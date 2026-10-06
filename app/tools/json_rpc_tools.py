from app.json_rpc import JSONRPCToolRouter


# ============================================================
# TRAVEL TOOLS
# ============================================================

def search_flights(
    origin: str,
    destination: str,
    date: str,
    passengers: int
) -> dict:
    """
    Search available flights between two cities.
    """

    return {
        "status": "success",
        "flights": [
            {
                "flight_id": "F001",
                "airline": "IndiGo",
                "origin": origin,
                "destination": destination,
                "date": date,
                "departure": "08:00",
                "arrival": "10:30",
                "price": 4500
            }
        ]
    }


def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int
) -> dict:
    """
    Search available hotels at the destination.
    """

    return {
        "status": "success",
        "hotels": [
            {
                "hotel_id": "H002",
                "name": "Palm Paradise Hotel",
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "price_per_night": 2800,
                "rating": 4.2
            }
        ]
    }


def search_activities(
    destination: str,
    preferences: list[str]
) -> dict:
    """
    Search activities based on travel preferences.
    """

    return {
        "status": "success",
        "activities": [
            {
                "activity_id": "A001",
                "name": "Beach Visit",
                "destination": destination,
                "preferences": preferences,
                "price": 500
            }
        ]
    }


def calculate_budget(
    flight_cost: float,
    hotel_cost: float,
    activity_cost: float,
    food_cost: float,
    transport_cost: float,
    budget: float
) -> dict:
    """
    Calculate total trip cost and compare it with budget.
    """

    total_cost = (
        flight_cost
        + hotel_cost
        + activity_cost
        + food_cost
        + transport_cost
    )

    return {
        "status": "success",
        "total_cost": total_cost,
        "budget": budget,
        "within_budget": total_cost <= budget
    }


# ============================================================
# ROUTER
# ============================================================

router = JSONRPCToolRouter()


router.register_tool(
    "search_flights",
    search_flights
)

router.register_tool(
    "search_hotels",
    search_hotels
)

router.register_tool(
    "search_activities",
    search_activities
)

router.register_tool(
    "calculate_budget",
    calculate_budget
)