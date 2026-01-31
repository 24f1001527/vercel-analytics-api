from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# 🔷 Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# 🔷 Load telemetry.json from REPO ROOT
# __file__ = /var/task/api/index.py
# parents[1] = /var/task (repo root)
DATA_FILE = Path(__file__).resolve().parents[1] / "telemetry.json"

telemetry = json.loads(DATA_FILE.read_text())

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
            "breaches": sum(l > threshold for l in latencies)
        }

    return result

