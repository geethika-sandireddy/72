"""Operational storm dynamics: optical-flow-like motion and lightning jumps.

The implementation is dependency-light: it estimates motion from centroids/fields and
keeps the contract compatible with replacing this estimator with Farneback/Lucas-Kanade
when OpenCV is available. It never labels the estimate as a physical wind field.
"""
from dataclasses import dataclass, asdict
from typing import Optional, Sequence
import numpy as np

@dataclass
class MotionEstimate:
    dy: float; dx: float; speed_pixels_per_frame: float; divergence: float; curl: float
    method: str = "centroid-prototype"
    def as_dict(self): return asdict(self)

def estimate_motion(previous: Optional[np.ndarray], current: np.ndarray) -> MotionEstimate:
    cur=np.asarray(current,float)
    if previous is None: return MotionEstimate(0.,0.,0.,0.,0.)
    old=np.asarray(previous,float)
    def centre(a):
        w=np.clip(a-nanmin(a),0,None); total=w.sum()
        if total<=1e-9: return np.array(a.shape)/2
        yy,xx=np.indices(a.shape); return np.array([(yy*w).sum()/total,(xx*w).sum()/total])
    delta=centre(cur)-centre(old); speed=float(np.linalg.norm(delta))
    return MotionEstimate(float(delta[0]),float(delta[1]),speed,0.,0.)

def nanmin(a):
    return float(np.nanmin(a)) if np.isfinite(a).any() else 0.

@dataclass
class LightningJump:
    current_rate: float; baseline_rate: float; z_score: float; jump: bool; window_minutes: int
    def as_dict(self): return asdict(self)

def lightning_jump(rates: Sequence[float], sigma_threshold: float=2.0, window_minutes: int=5) -> LightningJump:
    values=np.asarray(list(rates),float)
    if not len(values): return LightningJump(0.,0.,0.,False,window_minutes)
    current=float(values[-1]); history=values[:-1]
    baseline=float(history.mean()) if len(history) else current
    std=float(history.std(ddof=1)) if len(history)>1 else max(abs(baseline)*.25,1.)
    z=(current-baseline)/max(std,1e-6)
    return LightningJump(current,baseline,float(z),bool(z>=sigma_threshold),window_minutes)
