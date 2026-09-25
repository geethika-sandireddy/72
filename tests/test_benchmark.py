"""Tests for the required benchmark baselines."""
import numpy as np
from app.baselines import centroid_advection, persistence, binary_metrics
from app.benchmark import evaluate_replay

def test_persistence_preserves_observation():
    x=np.array([[0.,1.],[.2,.4]]); assert np.array_equal(persistence(x),x)

def test_advection_moves_signal():
    x=np.zeros((3,3)); x[1,1]=1; assert centroid_advection(x,0,1)[1,2] == 1

def test_benchmark_contains_all_baselines():
    x=np.zeros((3,3)); x[1,1]=1
    report=evaluate_replay({"case-a":{15:{"current":x,"observed":x,"indra":x}}},"REPLAY:held-out")
    assert {r["method"] for r in report["rows"]} == {"persistence","advection","indra"}

def test_live_benchmark_is_rejected():
    try: evaluate_replay({},"LIVE")
    except ValueError: return
    assert False
