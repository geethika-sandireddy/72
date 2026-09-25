"""Learned, multi-horizon probabilistic fusion head.

This is a compact sklearn reference implementation for the prototype. It is deliberately
trained only from explicitly labelled REPLAY/SYNTHETIC data; LIVE records are never used
silently as training data. Replace with a saved PyTorch MLP/GRU checkpoint for operations.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Sequence
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

@dataclass
class TrainingReport:
    trained: bool
    n_samples: int
    provenance: str
    model_version: str
    note: str
    def as_dict(self): return asdict(self)

class FusionMLP:
    HORIZONS = (5, 15, 30, 60, 180)
    def __init__(self, seed=26072):
        self.seed=seed; self.scaler=StandardScaler(); self.models={}; self.trained=False
        self.report=TrainingReport(False,0,"UNTRAINED","lad-fusion-v1","fit() is required")
    def fit(self, x: Sequence[Sequence[float]], labels: Dict[int, Sequence[int]], provenance: str):
        if provenance == "LIVE": raise ValueError("LIVE data cannot be used as training provenance")
        x=np.asarray(x,float); self.scaler.fit(x); z=self.scaler.transform(x)
        for h in self.HORIZONS:
            y=np.asarray(labels[h],int)
            if len(np.unique(y)) < 2: raise ValueError(f"horizon {h} requires both event classes")
            self.models[h]=MLPClassifier(hidden_layer_sizes=(24,12),solver="lbfgs",max_iter=500,random_state=self.seed+h).fit(z,y)
        self.trained=True; self.report=TrainingReport(True,len(x),provenance,"lad-fusion-v1","learned MLP heads; not a claimed real-data score")
        return self.report
    def predict(self, x: Sequence[float]) -> Dict[int,float]:
        if not self.trained: raise RuntimeError("FusionMLP has no trained checkpoint")
        z=self.scaler.transform(np.asarray(x,float).reshape(1,-1))
        return {h:float(self.models[h].predict_proba(z)[0,1]) for h in self.HORIZONS}

def calibrated_demo_model(seed=26072):
    """Return a deterministic, explicitly SYNTHETIC calibration model for the demo."""
    rng=np.random.default_rng(seed); x=rng.normal(size=(600,8)); signal=x[:,0]+.5*x[:,1]+.25*x[:,6]
    labels={h:(signal+rng.normal(0,1.0+np.log1p(h)/4,len(x))>0.8).astype(int) for h in FusionMLP.HORIZONS}
    model=FusionMLP(seed); model.fit(x,labels,"SYNTHETIC:calibration-v1"); return model
