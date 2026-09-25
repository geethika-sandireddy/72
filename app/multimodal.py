"""Explicit modality encoders and reliability-aware fusion features.

The prototype uses compact statistical encoders so it can run without a GPU. Each
modality has its own branch, mask and reliability score; no source is represented
only by a presence bit. Replace the branch projections with CNN/ConvLSTM encoders
when raster training data are available.
"""
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence
import numpy as np
from app.spatial import normalize_grid

@dataclass
class ModalityEmbedding:
    name: str
    vector: np.ndarray
    evidence: float
    reliability: float
    available: bool
    detail: Dict[str, float]

class ModalityEncoder:
    def __init__(self, name: str, expected: Sequence[str]): self.name=name; self.expected=tuple(expected)
    def encode(self, grids: Mapping[str, object], events=(), now=None) -> ModalityEmbedding:
        arrays=[]; details={}
        for product, obs in grids.items():
            try:
                a=normalize_grid(obs.values); arrays.append(a)
                details[f"{product}_mean"]=float(np.nanmean(a)); details[f"{product}_max"]=float(np.nanmax(a))
            except (AttributeError, ValueError, TypeError): continue
        if not arrays:
            return ModalityEmbedding(self.name,np.zeros(8),0.,0.,False,{})
        stack=np.concatenate([a.ravel() for a in arrays]); vector=np.array([
            float(np.mean(stack)), float(np.std(stack)), float(np.quantile(stack,.75)),
            float(np.quantile(stack,.95)), float(np.max(stack)), float(np.mean(stack>.7)),
            float(np.mean(stack<.2)), float(len(arrays)/max(len(self.expected),1))])
        evidence=float(np.clip(.35*vector[0]+.25*vector[2]+.40*vector[5],0,1))
        return ModalityEmbedding(self.name,vector,evidence,1.,True,details)

class LightningEncoder(ModalityEncoder):
    def encode(self, grids, events=(), now=None):
        if not events: return ModalityEmbedding(self.name,np.zeros(8),0.,0.,False,{})
        counts=[]
        for minutes in (5,15,30,60):
            counts.append(sum(1 for e in events if now is None or 0 <= (now-e.timestamp_utc).total_seconds()/60 <= minutes))
        scale=max(max(counts),1); vector=np.array([min(c/scale,1.) for c in counts]+[
            min(counts[0]/10,1.), min(counts[1]/20,1.), min(counts[2]/40,1.), min(counts[3]/80,1.)])
        evidence=float(np.clip(.5*vector[0]+.3*vector[1]+.2*vector[2],0,1))
        return ModalityEmbedding(self.name,vector,evidence,1.,True,{f"flash_count_{w}m":float(c) for w,c in zip((5,15,30,60),counts)})

class ReliabilityFusion:
    """Fuse independent evidence after normalization; availability != agreement."""
    def __init__(self):
        self.encoders={"radar":ModalityEncoder("radar",("ppi_z","max_z","ppi_v","sri")),"satellite":ModalityEncoder("satellite",("tir1","tir2","wv","cmv")),"nwp":ModalityEncoder("nwp",("temperature","rh","wind","cape","cin","shear")),"lightning":LightningEncoder("lightning",())}
    def encode(self, radar, satellite, nwp, lightning, now=None):
        embeddings=[self.encoders["radar"].encode(radar,now=now),self.encoders["satellite"].encode(satellite,now=now),self.encoders["lightning"].encode({},lightning,now),self.encoders["nwp"].encode(nwp,now=now)]
        present=[e for e in embeddings if e.available]; evidence=np.array([e.evidence for e in present])
        agreement=float(np.clip(1-np.std(evidence),0,1)) if len(evidence)>1 else (1. if len(evidence)==1 else 0.)
        availability=float(len(present)/4); vector=np.concatenate([e.vector for e in embeddings]+[[availability,agreement]])
        return vector, {e.name:{"available":e.available,"evidence":e.evidence,"reliability":e.reliability,"details":e.detail} for e in embeddings}, agreement
