"""TITAN-style prototype detector with gated nearest-neighbour track association."""
from dataclasses import dataclass, asdict
from typing import Dict, List
import numpy as np
from scipy import ndimage
@dataclass
class StormCell:
    cell_id:int; centroid_y:float; centroid_x:float; area:int; max_reflectivity:float
    motion_y:float=0.; motion_x:float=0.; area_growth:float=0.; max_reflectivity_trend:float=0.; provenance:str="SYNTHETIC"
    def as_dict(self): return asdict(self)
class StormCellTracker:
    def __init__(self, threshold_dbz=35., min_area=3, max_match_distance=20.):
        self.threshold_dbz=threshold_dbz; self.min_area=min_area; self.max_match_distance=max_match_distance; self.previous=[]; self.next_id=1
    def detect(self, field, provenance):
        a=np.asarray(field,float); labels,n=ndimage.label(a>=self.threshold_dbz, structure=np.ones((3,3))); out=[]
        for label in range(1,n+1):
            y,x=np.where(labels==label)
            if len(x)>=self.min_area: out.append(StormCell(self.next_id,float(y.mean()),float(x.mean()),len(x),float(a[y,x].max()),provenance=provenance)); self.next_id+=1
        return out
    def update(self, field, provenance="SYNTHETIC"):
        current=self.detect(field,provenance); used=set()
        for cell in current:
            choices=[(old,(cell.centroid_y-old.centroid_y)**2+(cell.centroid_x-old.centroid_x)**2) for old in self.previous if old.cell_id not in used]
            if choices:
                old,d=min(choices,key=lambda z:z[1])
                if d <= self.max_match_distance**2:
                    used.add(old.cell_id); cell.motion_y=cell.centroid_y-old.centroid_y; cell.motion_x=cell.centroid_x-old.centroid_x; cell.area_growth=(cell.area-old.area)/max(old.area,1); cell.max_reflectivity_trend=cell.max_reflectivity-old.max_reflectivity
        self.previous=current; return current
    @staticmethod
    def features(cell): return {"cell_motion_y":cell.motion_y,"cell_motion_x":cell.motion_x,"cell_area":float(cell.area),"cell_area_growth":cell.area_growth,"max_reflectivity":cell.max_reflectivity,"max_reflectivity_trend":cell.max_reflectivity_trend}
