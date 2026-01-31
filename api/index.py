from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import statistics

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data once
with open("telemetry.json", "r") as f:
    DATA = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/analytics")
def analytics(body: RequestBody):
    result = {}

    for region in body.regions:
        records = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        if not latencies:
            continue

        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]
        avg_uptime = statistics.mean(uptimes)
        breaches = sum(1 for l in latencies if l > body.threshold_ms)

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return result

