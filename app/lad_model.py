"""Inspectable Leaky Accumulate-Discharge (LAD) electrical-convective state."""
from dataclasses import dataclass, asdict
from collections import deque
from typing import Dict, Sequence
import numpy as np

@dataclass
class LADState:
    pressure: float = 0.0
    accumulation: float = 0.0
    discharged: bool = False
    gamma: float = 0.95
    rho: float = 0.8
    proxy: float = 0.0
    provenance: str = "SYNTHETIC"
    def as_dict(self): return asdict(self)

class LADCell:
    """P_t = gamma P_(t-1) + f_theta(x_t); flash applies P_t <- P_t(1-rho)."""
    HORIZONS = (5, 15, 30, 60, 180)
    def __init__(self, gamma: float = .95, rho: float = .8, history: int = 6):
        if not .9 <= gamma <= .99 or not .6 <= rho <= 1.0: raise ValueError("LAD parameters outside required bounds")
        self.gamma, self.rho, self.history = gamma, rho, history
        self.pressure = 0.0; self.history_values = deque(maxlen=history); self.states = []
    def f_theta(self, x: Dict[str, float]) -> float:
        # Small non-negative feature map; replace with trained MLP/GRU weights in production.
        raw = (max(0, x.get("vil_trend", 0))*1.2 + max(0, x.get("echo_top_growth", 0))*2
               + max(0, -x.get("brightness_temp_trend", 0))*.5 + x.get("cape", 0)/1500
               + x.get("shear", 0)/30 + max(0, x.get("max_reflectivity_trend", 0))*.08)
        return float(np.log1p(np.exp(raw)) / 4)
    def step(self, x: Dict[str, float], flash: bool = False, provenance: str = "SYNTHETIC") -> LADState:
        inc = self.f_theta(x); self.pressure = self.gamma*self.pressure + inc
        if flash: self.pressure *= (1-self.rho)
        proxy = np.clip((x.get("vil", 0)/70 + x.get("echo_top_km", 0)/18 + x.get("cape", 0)/3500)/3, 0, 1)
        state = LADState(self.pressure, inc, flash, self.gamma, self.rho, float(proxy), provenance)
        self.history_values.append(self.pressure); self.states.append(state); return state
    def forecast(self, x: Dict[str, float]) -> Dict[int, Dict[str, float]]:
        h = np.array(list(self.history_values) or [self.pressure])
        # sigmoid head g_phi(P_t, history, x_t), with uncertainty interval for demo.
        score = float(.55*self.pressure + .25*h.mean() + .2*self.f_theta(x))
        out = {}
        for minutes in self.HORIZONS:
            decay = np.exp(-minutes/240)
            lightning = float(1/(1+np.exp(-(score*decay-1.2))))
            thunderstorm = float(1/(1+np.exp(-(score*decay-.8))))
            spread = min(.25, .05 + .15/np.sqrt(max(len(h), 1)))
            out[minutes] = {"lightning_probability": lightning, "thunderstorm_probability": thunderstorm,
                            "lightning_lower": max(0, lightning-spread), "lightning_upper": min(1, lightning+spread),
                            "pressure": self.pressure, "pressure_history": h.tolist()}
        return out
    def proxy_regularizer(self) -> float:
        if not self.states: return 0.0
        p = np.array([s.pressure for s in self.states]); q = np.array([s.proxy for s in self.states])
        return float(np.mean((p/(p.max()+1e-6)-q)**2))
