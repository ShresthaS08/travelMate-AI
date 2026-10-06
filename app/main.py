from fastapi import FastAPI
from pydantic import BaseModel

from app.graph import travelmate_graph


app = FastAPI(
    title="TravelMate AI",
    description="AI-powered travel planning and booking agent",
    version="1.0.0"
)


class TravelRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    passengers: int
    budget: float | None = None
    preferences: list[str] = []
    booking_requested: bool = False


@app.get("/")
def root():
    return {
        "service": "TravelMate AI",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/travel")
def travel(request: TravelRequest):

    initial_state = {
        "messages": [],

        "origin": request.origin,
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,

        "passengers": request.passengers,
        "budget": request.budget,
        "preferences": request.preferences,

        "booking_requested": request.booking_requested,

        "decision_type": None,
        "decision_content": None,

        "tool_name": None,
        "tool_args": {},

        "tool_result": None,
        "tool_results": {},

        "executed_tools": [],

        "selected_flight": None,
        "selected_hotel": None,
        "selected_activities": [],

        "itinerary": None,

        "requires_approval": False,
        "approval_status": None,
        "pending_action": None,

        "error": None,

        "step_count": 0
    }

    config = {
        "configurable": {
            "thread_id": f"travel-{request.destination}"
        }
    }

    result = travelmate_graph.invoke(
        initial_state,
        config
    )

    return {
        "status": "success",
        "result": result
    }