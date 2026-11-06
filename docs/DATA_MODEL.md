# Data model

## 1. Canonical records
```python
class Sample(BaseModel):  vehicle_id: str; ts_ms: int; signal: str; value: float; quality: Literal["good","stale","invalid"]="good"
class LogLine(BaseModel): vehicle_id: str; ts_ms: int; source: str; severity: Literal["debug","info","warn","error"]; tag: str; text: str
class DtcRecord(BaseModel): vehicle_id: str; ts_ms: int; code: str; status: Literal["set","cleared","pending"]; freeze_frame: dict[str,float]
```
Enum signals are stored as numeric codes with a lookup in the signal catalogue.

## 2. Signal catalogue (seed in `vgpt/common/signals.yaml`)
Columns: name, unit, source, native rate, agg (how 1 Hz is built), deadband.
| Signal | Unit | Source | Rate | Agg | Deadband |
|---|---|---|---|---|---|
| vehicle_speed | km/h | CAN | 10 Hz | mean | 0.5 |
| accel_pedal, brake_pedal | % | CAN | 10 Hz | mean | 1 |
| gear (P,R,N,D) | enum | CAN | 1 Hz | last | 0 |
| odometer | km | CAN | 1 Hz | last | 0.01 |
| motor_power_kw, regen_power_kw | kW | CAN | 10 Hz | mean | 0.5 |
| energy_wh_per_km (derived, rolling 1 km) | Wh/km | derived | 1 Hz | mean | 2 |
| soc_pct | % | CAN | 1 Hz | last | 0.1 |
| range_est_km | km | CAN | 1 Hz | last | 1 |
| pack_voltage_v, pack_current_a | V, A | CAN | 10 Hz | mean | 0.5, 0.5 |
| pack_temp_max_c, pack_temp_min_c | C | CAN | 1 Hz | max, min | 0.2 |
| cell_delta_mv | mV | CAN | 1 Hz | max | 1 |
| coolant_pump_duty_pct | % | CAN | 1 Hz | mean | 1 |
| charge_state (none, ac, dc) | enum | CAN | 1 Hz | last | 0 |
| charge_power_kw | kW | CAN | 1 Hz | mean | 0.5 |
| aux_12v_voltage | V | CAN | 1 Hz | min | 0.05 |
| ambient_temp_c, cabin_temp_c | C | VHAL | 1 Hz | mean | 0.2 |
| hvac_power_kw | kW | CAN | 1 Hz | mean | 0.1 |
| hvac_mode (off, cool, heat) | enum | VHAL | 1 Hz | last | 0 |
| tyre_pressure_fl, _fr, _rl, _rr | bar | CAN | 1 Hz | mean | 0.01 |
| adas_lka_state (off, standby, active, disengaged) | enum | SOME/IP | 10 Hz | last | 0 |
| adas_disengage_reason (none, driver_override, low_confidence, sensor_loss, odd_exit) | enum | SOME/IP | event | last | 0 |
| camera_lane_conf_pct | % | SOME/IP | 10 Hz | mean | 1 |
| front_obj_dist_m | m | SOME/IP | 10 Hz | min | 0.5 |
| driver_hands_on | bool | SOME/IP | 10 Hz | last | 0 |
| gnss_geohash5 (text, coarse) | text | VHAL | 1 Hz | last | n/a |
| road_type (city, highway, other; derived from speed profile) | enum | derived | 1 Hz | last | 0 |
Diagnostics come as `DtcRecord`; QNX/syslog as `LogLine` (warn and above kept).
Add fuel signals (`fuel_level_pct`, `fuel_rate_lph`) only when an ICE profile is requested.

## 3. Stores and files (all under `VGPT_DATA_DIR`)
- `hot`: in-memory ring, raw native rate, 15 minutes.
- `warm.sqlite`: 1 Hz samples, 14 days. `meta.sqlite`: signals, events, insights, trips, FTS, black-box index. Black-box samples in `blackbox.sqlite`.

```sql
-- meta.sqlite
CREATE TABLE signal(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, unit TEXT, source TEXT NOT NULL,
  agg TEXT NOT NULL DEFAULT 'mean', kind TEXT NOT NULL DEFAULT 'numeric', deadband REAL DEFAULT 0, enum_json TEXT);
CREATE TABLE event(id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL, ts_ms INTEGER NOT NULL, type TEXT NOT NULL,
  severity TEXT NOT NULL, subject TEXT, source TEXT, payload_json TEXT, blackbox_status TEXT DEFAULT 'pending');
CREATE INDEX event_ts ON event(ts_ms); CREATE INDEX event_type_ts ON event(type, ts_ms);
CREATE TABLE insight(id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL, created_ms INTEGER NOT NULL, kind TEXT NOT NULL,
  severity TEXT NOT NULL, subject TEXT NOT NULL, title TEXT NOT NULL, narration TEXT, narration_source TEXT DEFAULT 'template',
  evidence_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued', delivered_ms INTEGER, dismissed_ms INTEGER, event_id TEXT REFERENCES event(id));
CREATE TABLE trip(id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL, start_ms INTEGER, end_ms INTEGER, distance_km REAL,
  energy_wh REAL, city_km REAL, highway_km REAL, city_wh_per_km REAL, highway_wh_per_km REAL);
CREATE TABLE suppression(subject TEXT PRIMARY KEY, until_ms INTEGER NOT NULL, dismiss_count INTEGER NOT NULL DEFAULT 0);
CREATE VIRTUAL TABLE doc_fts USING fts5(kind, ref UNINDEXED, text, tokenize='porter unicode61');
-- warm.sqlite
CREATE TABLE sample_1s(signal_id INTEGER NOT NULL, ts_ms INTEGER NOT NULL, value REAL NOT NULL, PRIMARY KEY(signal_id, ts_ms)) WITHOUT ROWID;
CREATE TABLE rollup_1m(signal_id INTEGER NOT NULL, ts_min INTEGER NOT NULL, n INTEGER, mean REAL, min REAL, max REAL, std REAL,
  PRIMARY KEY(signal_id, ts_min)) WITHOUT ROWID;
-- blackbox.sqlite
CREATE TABLE bb_sample(event_id TEXT NOT NULL, signal_id INTEGER NOT NULL, ts_ms INTEGER NOT NULL, value REAL NOT NULL,
  PRIMARY KEY(event_id, signal_id, ts_ms)) WITHOUT ROWID;
```
`vehicle_id` is reserved for fleet use; tables above omit it where one vehicle is assumed, but APIs and models carry it.

## 4. Write policy (decision D16)
- Warm tier writes a 1 Hz value only when |value minus last stored| exceeds the signal deadband, or every 60 s as a heartbeat. Readers forward-fill within 120 s; gaps beyond that are real gaps.
- Rollups: the writer maintains a running 1-minute aggregate per numeric signal and flushes at minute end.
- Black-box: on event at T, copy hot samples for T-60 s to T+60 s at native rate into `bb_sample` (schedule the post-event half using the clock). Mark `blackbox_status` pending then complete.

## 5. Retention
Parked-time job: delete warm rows older than 14 days in batches of 50k, then `PRAGMA incremental_vacuum`. Delete rollups older than 90 days. Never delete black-box windows linked to an event within 90 days. If disk use exceeds the cap (`warm+cold` 650 MB default), purge oldest warm first.

## 6. Size targets (verify in M8)
35 signals, 21 days: warm under 400 MB, cold under 250 MB. If missed, add block compression (zstd column blocks in BLOB) behind the `Store` interface; the poster's 90-day figure assumes that optimisation.

## 7. Baselines
`baseline(signal, state)` returns median and MAD over the previous 14 days for the same vehicle state (`driving`, `parked`, `charging_ac`, `charging_dc`), cached in memory, recomputed nightly. Used by contributors and drift detectors.
