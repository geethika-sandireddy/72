"""Case-separated replay benchmark for the judge demonstration.

The report is only a report when supplied with authorized replay arrays. It refuses
LIVE data and refuses to call a synthetic benchmark real validation.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Mapping, Sequence
import numpy as np
from app.baselines import binary_metrics, centroid_advection, persistence

@dataclass
class BenchmarkRow:
    case_id: str; horizon_minutes: int; method: str; metrics: dict
    def as_dict(self): return asdict(self)

def evaluate_replay(cases: Mapping[str, Mapping[int, Mapping[str, np.ndarray]]], provenance: str):
    if provenance == "LIVE": raise ValueError("benchmark requires held-out REPLAY cases, not LIVE data")
    rows=[]
    for case_id, horizons in cases.items():
        for horizon, sample in horizons.items():
            observed=np.asarray(sample["observed"],float); current=np.asarray(sample["current"],float)
            dy=float(sample.get("dy",0)); dx=float(sample.get("dx",0))
            predictions={"persistence":persistence(current),"advection":centroid_advection(current,dy,dx)}
            if "indra" in sample: predictions["indra"]=np.asarray(sample["indra"],float)
            for method,prediction in predictions.items(): rows.append(BenchmarkRow(case_id,int(horizon),method,binary_metrics(observed,prediction)).as_dict())
    return {"provenance":provenance,"case_count":len(cases),"rows":rows,"note":"Scores are valid only for authorized held-out cases with explicit label provenance."}
