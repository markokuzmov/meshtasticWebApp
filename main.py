from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. We updated this model to match what the listener is actually sending
class EnvironmentData(BaseModel):
    pressure: float
    temperature: float
    timestamp: str

flight_logs = []

@app.post("/api/telemetry")
def receive_telemetry(data: EnvironmentData):
    """The listener script will POST barometric data here."""
    flight_logs.append(data.model_dump())
    return {"status": "success", "message": "Environment telemetry received"}

@app.get("/api/telemetry", response_model=List[EnvironmentData])
def get_telemetry():
    """The Vite frontend will GET all data from this endpoint."""
    return flight_logs

@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    """Quick endpoint for the frontend to grab just the most recent update."""
    if not flight_logs:
        return {"status": "waiting", "message": "No data received yet"}
    return flight_logs[-1]