"""Spatial hazard fields and physically transparent feature aggregation."""
from typing import Dict, Iterable, List, Tuple
import numpy as np

def to_array(values):
    a=np.asarray(values,dtype=float)
    if a.ndim!=2 or min(a.shape)<1: raise ValueError("grid must be a non-empty 2-D array")
    return a

def lightning_density(events, meta, windows=(5,15,30,60)):
    out={w:np.zeros((meta.ny,meta.nx),dtype=float) for w in windows}
    latest=meta.timestamp_utc
    for event in events:
        age=(latest-event.timestamp_utc).total_seconds()/60
        if age<0: continue
        y=int(np.clip((event.latitude-meta.lat_min)/max(meta.lat_max-meta.lat_min,1e-9)*(meta.ny-1),0,meta.ny-1))
        x=int(np.clip((event.longitude-meta.lon_min)/max(meta.lon_max-meta.lon_min,1e-9)*(meta.nx-1),0,meta.nx-1))
        for w in windows:
            if age<=w: out[w][y,x]+=1
    return out

def normalize_grid(values):
    a=to_array(values); lo,hi=np.nanpercentile(a,[1,99]); return np.clip((a-lo)/max(hi-lo,1e-6),0,1)

def probability_fields(base: float, shape: Tuple[int,int], motion=(0.,0.), disagreement=0.):
    """Prototype spatial field: Gaussian around the current cell/feature centroid.
    This is a serving fallback; learned raster heads should replace it for operational use.
    """
    ny,nx=shape; yy,xx=np.mgrid[0:ny,0:nx]; cy, cx=ny/2+motion[0], nx/2+motion[1]
    sigma=max(min(ny,nx)/4,1); field=np.exp(-((yy-cy)**2+(xx-cx)**2)/(2*sigma*sigma))*base
    spread=.06+.20*disagreement
    return {"probability":field.tolist(),"lower":np.clip(field-spread,0,1).tolist(),"upper":np.clip(field+spread,0,1).tolist()}
