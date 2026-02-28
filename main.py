import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

class EnvironmentData(BaseModel):
    pressure: float
    temperature: float
    timestamp: str

LOG_FILE = "flight_logs.json"

# Load existing data when the server starts, or create an empty list
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        flight_logs = json.load(f)
else:
    flight_logs = []

def save_logs_to_disk():
    """Helper function to write the current memory to the JSON file."""
    with open(LOG_FILE, "w") as f:
        json.dump(flight_logs, f, indent=4)

@app.get("/")
def serve_frontend():
    """Serves the frontend dashboard on the root URL."""
    return FileResponse("index.html")

@app.post("/api/telemetry")
def receive_telemetry(data: EnvironmentData):
    """The listener script will POST barometric data here."""
    # Append the new data to our list
    flight_logs.append(data.model_dump())
    
    # Immediately save the updated list to the hard drive
    save_logs_to_disk()
    
    return {"status": "success", "message": "Environment telemetry saved to disk"}

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