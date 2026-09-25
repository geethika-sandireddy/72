# INDRA — SIH PS 26072

INDRA is a provenance-first, reliability-aware convective intelligence prototype for
0–3 hour thunderstorm and lightning nowcasting.

## Why this is different

Most weather demos stop at `data → model → map`. INDRA exposes the operational chain:

`source health → QC/evidence → storm object → LAD state → separate hazard forecasts → baseline comparison → impact decision → human review → replay verification`.

The scientific acceptance test is explicit: an authorized held-out replay must compare
INDRA against persistence and advection baselines using POD, FAR, CSI and ETS at each
forecast horizon. Synthetic mode is only for interaction/demo testing.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.service:app --reload
streamlit run app/dashboard.py
```

## Verification bundle

```bash
python scripts/run_benchmark.py data/authorized-benchmark --provenance REPLAY:held-out
pytest -q
```

A benchmark NPZ must contain `observed_<horizon>` and `current_<horizon>` arrays for
5, 15, 30, 60 and/or 180 minutes; optional `indra_<horizon>`, `dy_<horizon>`, and
`dx_<horizon>` arrays enable the model and advection comparisons.
