"""Kaggle submission entry point. Kept as a thin wrapper so the actual logic
lives in agent/policy.py and can be unit-tested independently.
"""
from agent.policy import agent as _agent


def agent(obs, config=None):
    return _agent(obs)
