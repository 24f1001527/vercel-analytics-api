from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# 🔷 CORS (explicit + permissive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# 🔷 Load telemetry.json from repo root
DATA_FILE = Path(__file__).resolve().parents[1] / "telemetry.json"
telemetry = json.loads(DATA_FILE.read_text())

# 🔷 Explicit OPTIONS handler (CRITICAL for checker)
@app.options("/analytics")
def analytics_options():
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

# 🔷 POST endpoint
@app.post("/analytics")
async def analytics(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies),
        }

    return result


