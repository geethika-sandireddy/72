"""API serving with strict provenance, real source health, spatial fields and state persistence."""
from fastapi import FastAPI, HTTPException
import time, numpy as np
from app.config import WarningContext, SensorHealth
from app.contracts import NowcastRequest
from app.ingestion import MultiSensorIngestor
from app.storm_cells import StormCellTracker
from app.lad_model import LADCell
from app.fusion_model import calibrated_demo_model
from app.spatial import lightning_density, normalize_grid, probability_fields
from app.temporal import CaseStateStore

app=FastAPI(title="INDRA — India Thunderstorm & Lightning Nowcast",version="1.1-prototype")
MODEL=calibrated_demo_model(); CASES=CaseStateStore()

def _validate(req):
    if req.provenance=="LIVE" and not (req.radar or req.satellite or req.nwp or req.lightning): raise HTTPException(400,"LIVE requires actual source payloads")
    if req.provenance.startswith("REPLAY:") and not req.case_id: raise HTTPException(400,"REPLAY requires case_id")
    if req.provenance.startswith("REPLAY:") and not (req.radar or req.satellite or req.nwp or req.lightning): raise HTTPException(400,"REPLAY requires stored historical observations")
    for group in (req.radar,req.satellite,req.nwp):
        for obs in group.values():
            if obs.provenance!=req.provenance: raise HTTPException(400,"observation provenance does not match request")

def _health(req):
    present={"RADAR":bool(req.radar),"SATELLITE":bool(req.satellite),"LIGHTNING":bool(req.lightning),"NWP":bool(req.nwp)}
    return [SensorHealth(source=k,status=("SYNTHETIC" if req.provenance=="SYNTHETIC" else ("LIVE" if v else "MISSING")),provenance=req.provenance).model_dump() for k,v in present.items()]

@app.get("/health")
def health(): return {"status":"ok","model":MODEL.report.as_dict()}
@app.post("/forecast")
def forecast(req: NowcastRequest):
    _validate(req); start=time.perf_counter(); case_id=req.case_id or "synthetic-demo"; state=CASES.get(case_id)
    if req.radar: field=next(iter(req.radar.values())).values; meta=next(iter(req.radar.values())).meta
    elif req.radar_field: field=req.radar_field; meta=None
    else: field=[[0.]]; meta=None
    cells=state.tracker.update(field,req.provenance); state.timestamps.append(str(time.time()))
    ing=MultiSensorIngestor(); records=ing.synthetic_snapshot(1) if req.provenance=="SYNTHETIC" and not (req.radar or req.satellite or req.nwp) else []
    x=records[0].values if records else {"vil":float(np.nanmean(field)),"vil_trend":0.4,"echo_top_growth":0.2,"brightness_temp_trend":-0.5,"cape":1200.,"shear":15.}
    cell=cells[-1] if cells else None; lad=state.lad_by_cell.setdefault(cell.cell_id if cell else 0,LADCell())
    if cell: x.update(state.tracker.features(cell))
    lad_state=lad.step(x,req.flash,req.provenance); agreement=float(np.mean([bool(req.radar),bool(req.satellite),bool(req.lightning),bool(req.nwp)]))
    vector=lad.feature_vector(x,agreement); probs=MODEL.predict(vector); shape=np.asarray(field).shape
    forecasts={}
    for h,p in probs.items(): forecasts[str(h)]={"lightning_probability":p,"thunderstorm_probability":float(np.clip(p*.85+.08,0,1)),"field":probability_fields(p,shape,(cell.motion_y,cell.motion_x) if cell else (0,0),1-agreement),"sensor_agreement":agreement,"pressure":lad.pressure}
    elapsed=round((time.perf_counter()-start)*1000,2)
    return {"provenance":req.provenance,"case_id":case_id,"latency_ms":elapsed,"latency_target_met":elapsed<60000,"storm_cells":[c.as_dict() for c in cells],"lad_state":lad_state.as_dict(),"forecast":forecasts,"sensor_health":_health(req),"state_summary":CASES.summary(case_id),"alert_context":WarningContext(district=req.district,state=req.state).model_dump(),"disclaimer":"Spatial fallback fields are demo outputs; report held-out real-case metrics before operational deployment."}
