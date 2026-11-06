---
description: Generate history from a scenario and inspect it against ground truth
---
Inputs: scenario name (default `demo_21d`), seed (default 7), mode (`backfill` or `live`).
1. Read `docs/SIMULATION.md`. Confirm the scenario file exists in `vgpt/sim/scenarios/`.
2. Reset data: `scripts/reset_data.sh` (ask before deleting a non-empty `data/` folder).
3. Run `python -m vgpt.sim.run --scenario <name> --mode <mode> --seed <seed>`.
4. Verify outputs: `data/ground_truth.json` exists; store size report is within `docs/DATA_MODEL.md` targets; event count matches ground truth.
5. Produce 4 plots (matplotlib, saved to `bench/results/plots/`): speed and SOC for one day, pack temperature across the fast-charge event, tyre pressures over 21 days, daily efficiency with the change-point.
6. Summarise in 10 lines: scenario, seed, duration, rows written, events, any mismatch with ground truth. Attach the plots as artifacts.
