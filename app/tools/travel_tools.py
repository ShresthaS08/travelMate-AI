def search_flights(
    origin: str,
    destination: str,
    date: str,
    passengers: int
) -> dict:

    flights = [
        {
            "flight_id": "AI101",
            "airline": "Air India",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "08:00",
            "arrival": "10:30",
            "price": 8500,
            "available_seats": 12
        },
        {
            "flight_id": "6E204",
            "airline": "IndiGo",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "11:30",
            "arrival": "14:00",
            "price": 7800,
            "available_seats": 8
        },
        {
            "flight_id": "QP301",
            "airline": "Akasa Air",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "16:00",
            "arrival": "18:30",
            "price": 8200,
            "available_seats": 5
        }
    ]

    # Make sure enough seats are available
    available_flights = [
        flight
        for flight in flights
        if flight["available_seats"] >= passengers
    ]

    return {
        "status": "success",
        "origin": origin,
        "destination": destination,
        "date": date,
        "passengers": passengers,
        "flights": available_flights
    }