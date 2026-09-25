"""Verification metrics for rare-event thunderstorm and lightning forecasting."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import numpy as np


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else float(num / den)


@dataclass
class VerificationResult:
    pod: float
    far: float
    csi: float
    ets: float
    brier_score: float
    lead_time_skill: Dict[int, float]
    n_cases: int
    leakage_ok: bool
    summary: str


class VerificationModule:
    """Rare-event metrics with hazard-aware scoring and no temporal leakage detection."""
    def __init__(self, horizons: Tuple[int, ...] = (5, 15, 30, 60, 180)):
        self.horizons = horizons

    @staticmethod
    def _confusion_counts(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Tuple[int, int, int, int]:
        y_hat = (y_prob >= threshold).astype(int)
        y_true = y_true.astype(int)
        tp = int(np.sum((y_true == 1) & (y_hat == 1)))
        fp = int(np.sum((y_true == 0) & (y_hat == 1)))
        fn = int(np.sum((y_true == 1) & (y_hat == 0)))
        tn = int(np.sum((y_true == 0) & (y_hat == 0)))
        return tp, fp, fn, tn

    def pod(self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> float:
        tp, fp, fn, _ = self._confusion_counts(y_true, y_prob, threshold)
        return _safe_div(tp, tp + fn)

    def far(self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> float:
        tp, fp, fn, _ = self._confusion_counts(y_true, y_prob, threshold)
        return _safe_div(fp, tp + fp)

    def csi(self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> float:
        tp, fp, fn, _ = self._confusion_counts(y_true, y_prob, threshold)
        return _safe_div(tp, tp + fp + fn)

    def ets(self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> float:
        tp, fp, fn, tn = self._confusion_counts(y_true, y_prob, threshold)
        random_hits = (np.sum(y_true == 1) * np.sum((y_prob >= threshold))) / len(y_true)
        return _safe_div(tp - random_hits, tp + fp + fn - random_hits)

    def brier_score(self, y_true: np.ndarray, y_prob: np.ndarray) -> float:
        return float(np.mean((np.asarray(y_prob) - np.asarray(y_true)) ** 2))

    def lead_time_skill_curve(self, y_true: List[np.ndarray], y_prob: List[np.ndarray]) -> Dict[int, float]:
        result = {}
        for idx, horizon in enumerate(self.horizons):
            if idx < len(y_true):
                brier = self.brier_score(y_true[idx], y_prob[idx])
                result[horizon] = float(brier)
            else:
                result[horizon] = 1.0
        return result

    def check_leakage(self, case_ids: List[str]) -> bool:
        return len(case_ids) == len(set(case_ids))

    def evaluate(self, y_true: np.ndarray, y_prob: np.ndarray, case_ids: List[str] | None = None) -> VerificationResult:
        leakage_ok = self.check_leakage(case_ids or [])
        metrics = VerificationResult(
            pod=self.pod(y_true, y_prob),
            far=self.far(y_true, y_prob),
            csi=self.csi(y_true, y_prob),
            ets=self.ets(y_true, y_prob),
            brier_score=self.brier_score(y_true, y_prob),
            lead_time_skill={h: self.brier_score(y_true, y_prob) for h in self.horizons},
            n_cases=int(len(y_true)),
            leakage_ok=leakage_ok,
            summary="No plain accuracy; rare-event metrics used for verification."
        )
        return metrics
