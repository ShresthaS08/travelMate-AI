from app.tools.travel_tools import search_flights


result = search_flights(
    origin="Delhi",
    destination="Goa",
    date="2026-11-10",
    passengers=2
)


print("\n========== FLIGHT SEARCH ==========\n")

print("Status:", result["status"])

print("Route:", result["origin"], "→", result["destination"])

print("Date:", result["date"])

print("Passengers:", result["passengers"])

print("\nAvailable Flights:")

for flight in result["flights"]:
    print(
        f"{flight['flight_id']} | "
        f"{flight['airline']} | "
        f"{flight['departure']} → {flight['arrival']} | "
        f"₹{flight['price']}"
    )