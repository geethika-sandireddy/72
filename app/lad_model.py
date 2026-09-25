"""Inspectable LAD state with multi-source agreement and horizon-aware heads."""
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
@dataclass
class LADState:
    pressure:float; accumulation:float; discharged:bool; gamma:float; rho:float; proxy:float; provenance:str
    def as_dict(self): return asdict(self)
class LADCell:
    HORIZONS=(5,15,30,60,180)
    def __init__(self,gamma=.95,rho=.8,history=6):
        if not .9<=gamma<=.99 or not .6<=rho<=1: raise ValueError("gamma/rho outside specification")
        self.gamma=gamma; self.rho=rho; self.pressure=0.; self.history_values=deque(maxlen=history); self.states=[]
    def f_theta(self,x):
        raw=max(0,x.get('vil_trend',0))*1.2+max(0,x.get('echo_top_growth',0))*2+max(0,-x.get('brightness_temp_trend',0))*.5+x.get('cape',0)/1500+x.get('shear',0)/30+max(0,x.get('max_reflectivity_trend',0))*.08
        return float(np.logaddexp(0,raw)/4)
    def step(self,x,flash=False,provenance='SYNTHETIC'):
        inc=self.f_theta(x); self.pressure=self.gamma*self.pressure+inc
        if flash: self.pressure*=1-self.rho
        proxy=float(np.clip((x.get('vil',0)/70+x.get('echo_top_km',0)/18+x.get('cape',0)/3500)/3,0,1)); state=LADState(self.pressure,inc,flash,self.gamma,self.rho,proxy,provenance); self.history_values.append(self.pressure); self.states.append(state); return state
    def feature_vector(self,x,agreement=1.): return [self.pressure,float(np.mean(self.history_values or [self.pressure])),x.get('vil_trend',0),x.get('echo_top_growth',0),x.get('brightness_temp_trend',0),x.get('cape',0)/3000,x.get('shear',0)/30,agreement]
    def proxy_regularizer(self):
        if not self.states:return 0.
        p=np.array([s.pressure for s in self.states]); q=np.array([s.proxy for s in self.states]); return float(np.mean((p/(p.max()+1e-6)-q)**2))
