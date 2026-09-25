"""Leakage-safe case-level splitting and per-horizon evaluation utilities."""
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, Sequence
import numpy as np
from app.metrics import VerificationModule

@dataclass
class ExperimentReport:
    split: Dict[str,int]
    leakage_ok: bool
    metrics: Dict[int,Dict[str,float]]
    baselines: Dict[str,Dict[int,float]]
    provenance: str
    def as_dict(self): return asdict(self)

def case_split(case_ids: Sequence[str], train_fraction=.7, validation_fraction=.15):
    cases=sorted(set(case_ids)); n=len(cases); a=max(1,int(n*train_fraction)); b=max(a+1,int(n*(train_fraction+validation_fraction)))
    return {"train":set(cases[:a]),"validation":set(cases[a:b]),"test":set(cases[b:])}

def evaluate_horizons(labels: Dict[int,Sequence[int]], predictions: Dict[int,Sequence[float]], case_ids: Sequence[str], split: Dict[str,set], provenance: str):
    test=set(split["test"]); idx=np.array([c in test for c in case_ids]); metrics={}
    for h,y in labels.items():
        y=np.asarray(y)[idx]; p=np.asarray(predictions[h])[idx]
        metrics[h]={"POD":VerificationModule.pod(y,p),"FAR":VerificationModule.far(y,p),"CSI":VerificationModule.csi(y,p),"ETS":VerificationModule.ets(y,p),"Brier":VerificationModule.brier_score(y,p)}
    return ExperimentReport({k:len(v) for k,v in split.items()},VerificationModule.leakage_check(split["train"],split["test"]) and VerificationModule.leakage_check(split["validation"],split["test"]),metrics,{},provenance)
