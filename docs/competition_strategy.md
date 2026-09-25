# Competition-grade extension layer

The current prototype now includes reusable building blocks inspired by the strongest competitor patterns, without claiming capabilities that have not been validated:

- `app/multimodal.py`: separate modality branches and evidence-aware fusion
- `app/qc.py`: pre-fusion grid quality checks
- `app/dynamics.py`: storm motion descriptor and lightning-jump detector
- `app/replay.py`: strict replay-case registry
- `app/impact.py`: probability-to-impact/arrival decision layer
- `app/audit.py`: SHA-256 audit records
- `app/ablation.py`: baseline/ablation artifact table

The strongest differentiator to demonstrate is not a generic dashboard. It is:

```text
quality control → time/space alignment → source evidence and availability
→ interpretable LAD state → independent lightning/thunderstorm heads
→ calibrated evaluation → impact/arrival decision support
```

Do not claim real-data skill, operational latency, or source ingestion until an authorized replay case is loaded and evaluated. The repository deliberately keeps restricted raw radar/satellite/lightning/NWP files out of git.
