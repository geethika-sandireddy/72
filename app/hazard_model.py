"""Independent lightning and thunderstorm heads with sequence-aware API."""
from dataclasses import dataclass, asdict
from typing import Dict, Sequence
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
@dataclass
class ModelReport:
    trained: bool; n_samples: int; provenance: str; version: str; feature_count: int
    def as_dict(self): return asdict(self)
class MultiHazardModel:
    HORIZONS=(5,15,30,60,180)
    def __init__(self,seed=26072):
        self.seed=seed; self.scaler=StandardScaler(); self.models={}; self.trained=False
        self.report=ModelReport(False,0,"UNTRAINED","indra-multimodal-v2",0)
    def fit(self,x,labels,provenance):
        if provenance=="LIVE": raise ValueError("LIVE observations cannot train a model")
        z=self.scaler.fit_transform(np.asarray(x,float)); self.models={}
        for hazard in ("lightning","thunderstorm"):
            self.models[hazard]={}
            for h in self.HORIZONS:
                y=np.asarray(labels[hazard][h],int)
                if len(np.unique(y))<2: raise ValueError(f"{hazard}/{h} needs both classes")
                self.models[hazard][h]=MLPClassifier((24,12),solver="lbfgs",max_iter=500,random_state=self.seed+h).fit(z,y)
        self.trained=True; self.report=ModelReport(True,len(x),provenance,"indra-multimodal-v2",z.shape[1]); return self.report
    def predict(self,x):
        if not self.trained: raise RuntimeError("no persisted trained model")
        z=self.scaler.transform(np.asarray(x,float).reshape(1,-1)); return {str(h):{"lightning_probability":float(self.models['lightning'][h].predict_proba(z)[0,1]),"thunderstorm_probability":float(self.models['thunderstorm'][h].predict_proba(z)[0,1])} for h in self.HORIZONS}
