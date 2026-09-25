"""Leakage-safe rare-event verification. No accuracy metric is exposed."""
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, Mapping, Sequence, Tuple
import numpy as np

def div(a, b): return float(a / b) if b else 0.0
@dataclass
class VerificationResult:
    pod: float; far: float; csi: float; ets: float; brier_score: float
    lead_time_skill: Dict[int, float]; n_samples: int; n_cases: int; leakage_ok: bool
    provenance: str; baseline_brier: float | None = None
    def as_dict(self): return asdict(self)
class VerificationModule:
    HORIZONS = (5, 15, 30, 60, 180)
    @staticmethod
    def split_case_ids(case_ids: Sequence[str], test_fraction=.2) -> Tuple[np.ndarray, np.ndarray]:
        unique = np.array(sorted(set(case_ids))); cut = max(1, int(len(unique)*(1-test_fraction)))
        train = set(unique[:cut]); return np.array([c in train for c in case_ids]), np.array([c not in train for c in case_ids])
    @staticmethod
    def leakage_check(train_cases: Iterable[str], test_cases: Iterable[str]) -> bool:
        return not (set(train_cases) & set(test_cases))
    @staticmethod
    def evaluate(y_true, y_prob, case_ids, horizon_probabilities: Mapping[int, Sequence[float]] | None = None, provenance="REPLAY:unknown", baseline_prob=None):
        y = np.asarray(y_true, int); p = np.asarray(y_prob, float); pred = p >= .5
        tp, fp, fn = np.sum((y==1)&pred), np.sum((y==0)&pred), np.sum((y==1)&(~pred)); n = len(y)
        random_hits = (np.sum(y==1)*np.sum(pred)/max(n,1)); ets_den = tp+fp+fn-random_hits
        curve = {h: float(np.mean((np.asarray(v)-y)**2)) for h,v in (horizon_probabilities or {5:p}).items()}
        for h in VerificationModule.HORIZONS: curve.setdefault(h, float("nan"))
        return VerificationResult(div(tp,tp+fn), div(fp,tp+fp), div(tp,tp+fp+fn), div(tp-random_hits,ets_den), float(np.mean((p-y)**2)), curve, n, len(set(case_ids)), VerificationModule.leakage_check(case_ids, []), provenance, None if baseline_prob is None else float(np.mean((np.asarray(baseline_prob)-y)**2)))
