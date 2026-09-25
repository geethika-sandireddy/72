# SIH 2026 PS 26072 — INDRA prototype

INDRA is a provenance-first, sensor-disagreement-aware prototype for 0–3 hour thunderstorm and lightning nowcasting over India.

## Run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.service:app --reload
# second terminal:
streamlit run app/dashboard.py
```

API docs: http://127.0.0.1:8000/docs

The default dashboard scenario is explicitly `SYNTHETIC`. `LIVE` mode rejects missing normalized sensor payloads rather than inventing observations. Real MOSDAC, GFS/ERA5, WWLLN/WGLC and ILLN adapters must be populated with authenticated/downloaded data before operational use.

## Scientific and engineering contract

- Separate connected-component storm-cell detection/tracking output and separate lightning/thunderstorm probabilities.
- LAD state is inspectable: `P_t = gamma P_(t-1) + f_theta(x_t)`, followed by flash discharge `P_t <- P_t(1-rho)`; `gamma` and `rho` are bounded by the PS.
- Learned MLP fusion heads produce distinct 5/15/30/60/180-minute probabilities. The bundled checkpoint is deterministic synthetic calibration, clearly reported as such—not a real-data score.
- Radar, satellite, lightning, and NWP are explicit normalized source contracts. No multi-radar fusion is claimed unless records from both radar sources are supplied.
- Confidence intervals widen as sensor agreement falls; the UI exposes health and provenance per source.
- Verification must be run on held-out storm cases using POD, FAR, CSI, ETS, Brier and per-horizon curves. Plain accuracy is intentionally absent.
- `train_demo.py` is only a smoke test. Do not report its output as operational skill.

## Data truthfulness

Every record and UI view carries `LIVE`, `REPLAY:<case-study>`, or `SYNTHETIC`. ILLN is not assumed to have a public bulk API. A synthetic fallback is allowed only when labelled SYNTHETIC everywhere. This repository does not claim 100% accuracy; atmospheric forecasts are probabilistic and must be validated against real held-out cases.

## Judge demo story

1. Show a synthetic replay with cell track, separate hazards, LAD pressure, confidence intervals and sensor provenance.
2. Disable/delay a source in a real adapter payload and show uncertainty widening.
3. Show the verification report from case-separated replay data; never use inference-time synthetic labels as evaluation evidence.
4. Position the district schema alongside IMD's existing product, not as a replacement.
