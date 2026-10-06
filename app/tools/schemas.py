flight_search_schema = {
    "name": "search_flights",
    "description": "Search available flights between two cities.",
    "input_schema": {
        "type": "object",
        "properties": {
            "origin": {
                "type": "string",
                "description": "Departure city"
            },
            "destination": {
                "type": "string",
                "description": "Arrival city"
            },
            "date": {
                "type": "string",
                "description": "Travel date in YYYY-MM-DD format"
            },
            "passengers": {
                "type": "integer",
                "description": "Number of passengers"
            }
        },
        "required": [
            "origin",
            "destination",
            "date",
            "passengers"
        ]
    }
}