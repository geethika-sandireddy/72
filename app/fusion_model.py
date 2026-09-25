"""A small learned fusion head around the inspectable LAD state."""
from dataclasses import dataclass
from typing import Dict, Iterable, Sequence
import numpy as np
from sklearn.neural_network import MLPClassifier

FEATURES = ("pressure", "pressure_mean", "vil_trend", "echo_top_growth", "brightness_temp_trend", "cape", "shear", "sensor_agreement")

@dataclass
class TrainingReport:
    trained: bool
    n_samples: int
    provenance: str
    note: str

class FusionMLP:
    """Learned probabilistic head; training provenance is exposed in every prediction."""
    def __init__(self, seed: int = 26072):
        self.model = MLPClassifier(hidden_layer_sizes=(16, 8), activation="relu", solver="lbfgs", random_state=seed, max_iter=300)
        self.trained = False; self.report = TrainingReport(False, 0, "UNTRAINED", "fit() must be called with case-separated data")
    def fit(self, x: Sequence[Sequence[float]], y: Sequence[int], provenance: str) -> TrainingReport:
        if provenance == "LIVE": raise ValueError("training provenance must identify replay or synthetic data")
        self.model.fit(np.asarray(x, dtype=float), np.asarray(y, dtype=int)); self.trained = True
        self.report = TrainingReport(True, len(y), provenance, "learned MLP fusion head")
        return self.report
    def predict(self, x: Sequence[Sequence[float]]) -> np.ndarray:
        if not self.trained: raise RuntimeError("FusionMLP is untrained; run train_demo.py or inject model weights")
        return self.model.predict_proba(np.asarray(x, dtype=float))[:, 1]
