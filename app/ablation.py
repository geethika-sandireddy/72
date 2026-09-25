"""Evaluation artifacts for competitor-grade baseline and ablation tables."""
from dataclasses import dataclass, asdict
from typing import Dict, Sequence
import numpy as np
from app.verification import score, best_threshold

@dataclass
class AblationRow:
    experiment: str; horizon: int; score: Dict[str,float]; note: str
    def as_dict(self): return asdict(self)

def compare(y: Sequence[int], predictions: Dict[str,Sequence[float]], horizon: int, validation_prediction=None):
    threshold=best_threshold(y,validation_prediction) if validation_prediction is not None else .5
    return [AblationRow(name,horizon,score(y,p,threshold).as_dict(),"Threshold selected on validation" if validation_prediction is not None else "Demo threshold; not a skill claim") for name,p in predictions.items()]
