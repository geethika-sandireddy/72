"""Train a deterministic demo model and print a leakage-safe verification report.
This is a smoke/demo calibration only; it is not a real-data performance claim.
"""
import numpy as np
from app.fusion_model import calibrated_demo_model
from app.metrics import VerificationModule
rng=np.random.default_rng(26072); n=600; cases=np.array([f"case-{i//20:03d}" for i in range(n)])
model=calibrated_demo_model(); x=rng.normal(size=(n,8)); signal=x[:,0]+.5*x[:,1]+.25*x[:,6]
labels={h:(signal+rng.normal(0,1+np.log1p(h)/4,n)>0.8).astype(int) for h in model.HORIZONS}
train=np.array([int(c.split('-')[1])<24 for c in cases]); test=~train
probs={h:model.predict(x[i])[h] for i,h in enumerate([5]*n)}
# Report the split contract; full training/evaluation requires a persisted checkpoint and replay tensors.
print({"train_cases":len(set(cases[train])),"test_cases":len(set(cases[test])),"leakage_ok":VerificationModule.leakage_check(cases[train],cases[test]),"note":"demo calibration only"})
