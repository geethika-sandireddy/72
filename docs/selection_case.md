# Why INDRA should be selected

## The problem NTRO is actually asking

This is not merely a dashboard problem. It is a verification problem: can a system
use heterogeneous atmospheric observations to produce a **gridded, probabilistic,
short-lead forecast** that beats simple persistence and motion baselines on an unseen
convective case?

## INDRA's defensible wedge

INDRA is designed around an operator trust loop:

```text
heterogeneous observations
→ quality/provenance/freshness
→ storm object + LAD state
→ separate lightning and thunderstorm probability fields
→ persistence/advection/INDRA comparison
→ source contribution and uncertainty
→ human review, not automatic official warning
```

The differentiator is not claiming a larger neural network. It is making every forecast
answerable:

- What was observed?
- What was missing or delayed?
- Which storm object drove the signal?
- How did the model compare with persistence and motion?
- What happens when a modality is removed?
- Can the result be replayed and audited?

## The judge demo

1. Launch the Earth Operations console in explicitly labelled `SYNTHETIC` mode.
2. Select a tracked cell and show its movement, growth, reflectivity and LAD pressure.
3. Select +15, +30 and +60 minutes and show separate hazard curves.
4. Open Evidence & Health: distinguish `availability` from `agreement`; show missing/delayed source state.
5. Open Forecaster Desk: record approve/edit/dismiss; emphasize no official warning is issued.
6. For the scientific proof, run `scripts/run_benchmark.py` on an authorized, case-separated replay bundle and show INDRA versus persistence and advection for POD/FAR/CSI/ETS.

## What we do not claim

No real-data skill, calibration, national coverage, official warning issuance, or live latency is claimed until the corresponding authorized replay artifact exists. This is a feature, not an embarrassment: it prevents a judge from finding a provenance loophole during questioning.
