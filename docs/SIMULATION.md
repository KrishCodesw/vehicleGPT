# Simulation

The simulator is the vehicle side. It is the only component that may transmit. It produces plausible signals from a physics-light model, injects faults, and emits ground truth for tests.

## 1. Modes
- `backfill`: simulated clock at max speed; samples go straight into the ingest pipeline as `Sample` objects (skipping wire encoding) except a configurable `--wire-fraction` (default 0.02) that goes through the real CAN/UDP path to exercise decoders.
- `live`: wall clock times a speed factor (1x, 10x, 60x); everything goes over the wire (CAN transport and UDP adapters).
- `replay`: ASC/BLF files via python-can (S priority).
Run: `python -m vgpt.sim.run --scenario demo_21d --mode backfill --seed 7`.

## 2. Vehicle model (EV default; parameters in `vgpt/sim/model/params.yaml`)
- Mass 1800 kg, CdA 0.65 m2, Crr0 0.009, battery 60 kWh, drivetrain efficiency 0.9, regen share 0.6 (scaled by `regen_limit`).
- Road power: `P = (m g Crr v + 0.5 rho CdA v^3 + m a v) / eta`, with `Crr = Crr0 (1 + k (p_nom - p)/p_nom)` so low tyre pressure raises consumption. Regen on negative power. Aux power includes HVAC: `P_hvac = c * |T_set - T_amb|` clipped to 0.3 to 4.5 kW.
- SOC integrates net power. `range_est_km = soc * capacity / EMA(Wh/km over last 50 km)`.
- Thermal: `C dT/dt = I^2 R + P_charge_loss - k_cool(duty) (T - T_cool) - k_amb (T - T_amb)`; pump duty rises with `(T - 30)`; above 45 C DC charge power derates. Warning threshold 45 C, critical 55 C.
- Charging: AC 7 kW overnight; DC fast up to 150 kW with a SOC taper and thermal derating.
- Tyres: `p = p_nom (T_amb + 273) / (T_ref + 273) - leak(t)`.
- ADAS lane-keep state machine: `camera_lane_conf = base - fade(segment) - glare(time of day) + noise`; disengage when conf is under 40% for 1.5 s (reason `low_confidence`), on steering override with hands on (`driver_override`), or on a dropout (`sensor_loss`).
- Trips: weekday commute (city 12 km at about 28 km/h with stops, highway 18 km at about 100 km/h) twice per day, plus random weekend trips. Route segments carry ids so faded-marking segments recur.

## 3. Scenario file
```yaml
name: demo_21d
seed: 7
start: 2026-10-10T00:00:00Z
days: 21
vehicle: ev_default
weather: {ambient_c: {start: 30, end: 22, noise: 1.5}}   # cooling trend drives HVAC and efficiency
profile: {commute: weekday, charge: {ac_overnight: true}}
inject:
  - {type: tyre_leak, tyre: rl, start_day: 3, bar_per_day: 0.02, days: 10}
  - {type: regen_limit_change, day: 12, factor: 0.85}
  - {type: lane_marking_fade, segment: SEG_HWY_07, days: [14,15,16,18,19], conf_drop: 45}
  - {type: sensor_loss, day: 19, at: "08:41", seconds: 3}
  - {type: fast_charge, day: 17, at: "14:24", ambient_c: 38, hvac: max, duration_min: 22}
  - {type: dtc_set, code: P0A7E, day: 17, at: "14:32", when: pack_temp_max_c>=45}
```
Shipped scenarios: `clean_21d` (no injections; false-alert gate), `range_decay`, `fast_charge_overtemp`, `adas_dropouts`, `city_vs_highway`, `demo_21d` (all injections combined).

## 4. Wire adapters (stand-ins for real stacks)
| Real stack | Stand-in | Format |
|---|---|---|
| CAN / CAN-FD | python-can bus via `VGPT_CAN_INTERFACE`; frames encoded with `vgpt/sim/dbc/vehicle.dbc` (author it; round-trip test with cantools) | CAN frames |
| SOME/IP | UDP 127.0.0.1:30509 | JSON `{service:0x1234,event:0x8001,ts_ms,fields:{...}}` |
| Android VHAL | UDP 127.0.0.1:30510 | JSON `{prop:"AMBIENT_TEMP",value:22.5,ts_ms}` |
| QNX slog2/syslog | UDP 127.0.0.1:5514 | RFC5424 lines |
| UDS/DoIP | UDP 127.0.0.1:30511 | JSON `{code,status,freeze_frame,ts_ms}` |
Message plan for the DBC (agent finalises ids and layouts): 0x100 Drive (speed, pedals, gear), 0x110 Power (motor, regen, voltage, current), 0x120 Battery (soc, temps, cell delta, pump duty), 0x130 Charge (state, power), 0x140 Climate (hvac power), 0x150 Tyres (4 pressures), 0x160 Body (aux 12 V, odometer), 0x170 Range. Rates follow `DATA_MODEL.md`.
Real adapters (vsomeip client, Cuttlefish VHAL, QNX forwarder) implement the same `SignalSource` Protocol and arrive in M9.

## 5. Ground truth (`data/ground_truth.json`, written on every run)
```json
{ "events":[{"type":"battery_temp_high","ts_ms":0,"peak":47.2,"rise_c":11.0,"rise_min":8}],
  "adas_disengagements":[{"ts_ms":0,"reason":"low_confidence","segment":"SEG_HWY_07"}],
  "changepoints":[{"signal":"energy_wh_per_km","day":12,"direction":"up","size_pct":6}],
  "range_decay":{"window_days":14,"contributors":{"ambient_temp":0.45,"hvac":0.30,"tyre_pressure":0.15,"other":0.10}},
  "segment_efficiency":{"city_wh_per_km":0,"highway_wh_per_km":0},
  "trips":[...] }
```
Contributor shares are computed from the model coefficients and applied changes, not hand-typed. Tests compare engine output to this file: changepoint within 1 day; top-3 contributors match as a set; event lists equal; segment efficiency within 3%.

## 6. Determinism
Seeded RNG only (`numpy.random.Generator`). Same scenario and seed give byte-identical ground truth and the same sample stream.

## 7. CARLA (M9, optional)
`vgpt/sim/carla_bridge.py` maps CARLA vehicle state and sensors to the same signal names and runs fault scripts through OpenSCENARIO. It must not be required for any test.
