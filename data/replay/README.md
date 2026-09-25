# Authorized replay data intake

Place only legitimately obtained, redistributable hackathon data under a case directory. Do not commit credentials or restricted raw files.

Expected layout:

```text
case_id/
  metadata.json
  radar/
    radar_1/<timestamp>.npz
    radar_2/<timestamp>.npz
  satellite/
    tir1/<timestamp>.npz
    tir2/<timestamp>.npz
    water_vapour/<timestamp>.npz
    cmv/<timestamp>.npz
  lightning/<timestamp>.csv
  nwp/
    <model>/<variable>/<timestamp>.npz
  labels/
    future_radar/<timestamp>.npz
    future_lightning/<timestamp>.csv
```

Every case must contain a `metadata.json` with:

- `case_id`
- `provenance`, exactly `REPLAY:<case_id>`
- `sources`
- `domain` and grid metadata
- `master_cadence_minutes`
- `observation_start_utc` and `observation_end_utc`
- `license_or_access_note`
- `raw_data_owner`

The validator checks structure and metadata only. It does not claim that a file is official or real based on its filename.
