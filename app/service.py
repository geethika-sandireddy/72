"""API service and latency logging for the nowcasting prototype."""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Any
import time

from app.config import WarningContext
from app.ingestion import MultiSensorIngestor
from app.storm_cells import StormCellTracker
from app.lad_model import LADCell
from app.metrics import VerificationModule

app = FastAPI(title="SIH 2026 PS 26072 – Thunderstorm and Lightning Nowcasting")

class ForecastRequest(BaseModel):
    radar_field: List[List[float]]
    provenance: str = "LIVE"

@app.get("/health")
def health():
    return {"status": "ok", "service": "thunderstorm-lightning-nowcast"}

@app.post("/forecast")
def forecast(req: ForecastRequest):
    start = time.perf_counter()
    ingestor = MultiSensorIngestor()
    tracker = StormCellTracker()
    lad = LADCell()
    metrics = VerificationModule()

    snaps = ingestor.synthetic_snapshot(cells=4, provenance=req.provenance)
    features = []
    for rec in snaps:
        features.append(rec.values)
        lad.step(rec.values, flash=bool(rec.values.get("flash", 0)), provenance=req.provenance)
    forecast_output = lad.forecast(features[-1] if features else {})
    verification = metrics.evaluate(
        y_true=[1 if rec.values.get("flash", 0) else 0 for rec in snaps],
        y_prob=[forecast_output[5]["lightning_probability"] for _ in snaps],
        case_ids=[req.provenance for _ in snaps],
    )
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return {
        "provenance": req.provenance,
        "latency_ms": elapsed_ms,
        "storm_cells": tracker.detect(req.radar_field, req.provenance) if req.radar_field else [],
        "lad_state": lad.states[-1].as_dict() if lad.states else {},
        "forecast": forecast_output,
        "verification": verification.__dict__,
        "alert_context": WarningContext(district="Patna", state="Bihar").model_dump(),
    }

@app.get("/district-warning")
def district_warning():
    return WarningContext(district="Patna", state="Bihar").model_dump()
