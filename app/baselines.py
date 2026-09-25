"""Required nowcasting baselines: persistence and centroid advection.

Both baselines operate on a probability/intensity grid and preserve its shape. They
are deliberately deterministic so a replay report can compare INDRA against the
same cases and horizons without moving-target demo numbers.
"""
from __future__ import annotations
import numpy as np

def persistence(field, steps: int = 1):
    """Last-observation baseline; `steps` is retained for a stable API."""
    return np.asarray(field, dtype=float).copy()

def centroid_advection(field, dy: float = 0.0, dx: float = 0.0):
    """Translate a field using nearest-neighbour advection with zero fill.

    This is an intentionally transparent optical-flow/advection proxy. It is not
    presented as a substitute for a trained optical-flow implementation.
    """
    source = np.asarray(field, dtype=float)
    result = np.zeros_like(source)
    sy = int(round(dy)); sx = int(round(dx))
    y0=max(0,sy); y1=source.shape[0]+min(0,sy); x0=max(0,sx); x1=source.shape[1]+min(0,sx)
    result[y0:y1,x0:x1] = source[y0-sy:y1-sy,x0-sx:x1-sx]
    return result

def binary_metrics(observed, predicted, threshold: float = .5):
    y=np.asarray(observed,float)>=threshold; p=np.asarray(predicted,float)>=threshold
    tp=int(np.sum(y&p)); fp=int(np.sum(~y&p)); fn=int(np.sum(y&~p))
    div=lambda a,b: float(a/b) if b else 0.0
    random_hits=float(y.sum()*p.sum()/max(y.size,1)); denom=tp+fp+fn-random_hits
    return {"pod":div(tp,tp+fn),"far":div(fp,tp+fp),"csi":div(tp,tp+fp+fn),"ets":div(tp-random_hits,denom)}
