"""Persistent model artifact loader; never retrains silently at API startup."""
from pathlib import Path
import joblib
MODEL_DIR=Path("models")
def save(model,path=MODEL_DIR/"indra.joblib"):
    Path(path).parent.mkdir(parents=True,exist_ok=True); joblib.dump(model,path); return str(path)
def load(path=MODEL_DIR/"indra.joblib"):
    if not Path(path).exists(): return None
    return joblib.load(path)
