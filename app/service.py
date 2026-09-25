"""Operational nowcast service: real payloads in, clearly tagged fallback only."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import time, numpy as np
from app.config import WarningContext, SensorHealth
from app.ingestion import MultiSensorIngestor
from app.storm_cells import StormCellTracker
from app.lad_model import LADCell
from app.fusion_model import calibrated_demo_model
from app.metrics import VerificationModule

app=FastAPI(title="INDRA — India Thunderstorm & Lightning Nowcast", version="1.0-prototype")
MODEL=calibrated_demo_model()
class ForecastRequest(BaseModel):
    radar_field: List[List[float]] = Field(default_factory=list)
    provenance: str = "SYNTHETIC"
    case_id: Optional[str] = None
    district: str = "Patna"; state: str = "Bihar"
    sensor_payload: Optional[Dict[str, Dict[str,float]]] = None
    flash: bool = False

@app.get("/health")
def health(): return {"status":"ok","service":"indra-nowcast","model":MODEL.report.as_dict()}

@app.post("/forecast")
def forecast(req: ForecastRequest):
    if req.provenance == "LIVE" and not req.sensor_payload:
        raise HTTPException(400,"LIVE requires normalized sensor_payload; use SYNTHETIC for the demo fallback")
    start=time.perf_counter(); ingestor=MultiSensorIngestor(); tracker=StormCellTracker(); lad=LADCell()
    if req.sensor_payload: records=ingestor.normalize_payload(req.sensor_payload,req.provenance); merged={k:v for r in records for k,v in r.values.items()}
    else: records=ingestor.synthetic_snapshot(4); merged=records[-1].values
    cells=tracker.update(req.radar_field or [[0]],req.provenance)
    if cells: merged.update(tracker.features(cells[-1]))
    agreement=float(1-np.std([merged.get("vil_trend",0),merged.get("echo_top_growth",0),-merged.get("brightness_temp_trend",0)]))
    agreement=float(np.clip(agreement,0,1)); lad_state=lad.step(merged,req.flash,req.provenance)
    vector=lad.feature_vector(merged,agreement); probabilities=MODEL.predict(vector)
    forecasts={str(h):{"lightning_probability":p,"thunderstorm_probability":float(np.clip(p+.08,0,1)),"confidence_interval":[max(0,p-(.06+.20*(1-agreement))),min(1,p+(.06+.20*(1-agreement)))],"sensor_agreement":agreement,"pressure":lad.pressure} for h,p in probabilities.items()}
    elapsed=round((time.perf_counter()-start)*1000,2)
    return {"provenance":req.provenance,"case_id":req.case_id,"latency_ms":elapsed,"latency_target_met":elapsed<60000,
      "storm_cells":[c.as_dict() for c in cells],"lad_state":lad_state.as_dict(),"forecast":forecasts,
      "model":MODEL.report.as_dict(),"sensor_health":[SensorHealth(source=s,status=("SYNTHETIC" if req.provenance=="SYNTHETIC" else "LIVE"),provenance=req.provenance).model_dump() for s in ("MOSDAC_RADAR","MOSDAC_INSAT","GFS_ERA5","WWLLN_WGLC","ILLN")],
      "alert_context":WarningContext(district=req.district,state=req.state).model_dump(),"disclaimer":"Prototype output; verify against held-out real cases before operational use."}

@app.get("/district-warning")
def district_warning(district="Patna",state="Bihar"): return WarningContext(district=district,state=state).model_dump()
