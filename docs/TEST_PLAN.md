# Test plan

## 1. Pyramid
Unit (detectors, tools, verifier, store, policy, units) then integration (sim to ingest to store to insight with `FakeLLM`) then end to end (API + web with Playwright) then benchmarks (golden set, latency, memory, storage). Every layer runs on `FakeLLM`; model tests are a separate marked suite (`-m model`).

## 2. Golden set (`bench/golden/questions.yaml`)
Fields: `id, text, expected_intent, expected_plan_subset, must_cite_signals, expected_facts (refs into ground_truth.json), latency_budget_ms`. Start with 60 questions, grow to 200.
Core five (must pass):
1. "Why has my driving range reduced over the last two weeks?" (trend_explain; top contributors match ground truth)
2. "When did fuel efficiency show the largest drop?" (changepoint; EV wording "efficiency" and "fuel" both map to energy_wh_per_km; day within 1 of truth)
3. "Show all ADAS disengagement events from yesterday." (event_list; exact set)
4. "What happened before the battery overheating warning?" (pre_event_scan; fast charge in top 3)
5. "Compare energy consumption between city and highway driving." (compare_segments; within 3%)
Variants: paraphrases, typos, different windows ("last week", "since Monday"), follow-ups ("why?" with `insight_id`), out-of-scope ("what's the weather", "disable the warning"), ambiguous. About 25 percent are unsupported or adversarial.

## 3. Metrics and gates
| Metric | Gate |
|---|---|
| Intent accuracy | at least 95% |
| Evidence match (facts equal ground truth within tolerance) | at least 95% |
| Verifier escapes | 0 |
| Answer card latency p95 (`a55` container) | under 1 s |
| First token p95 | under 2 s |
| Event to template insight / model insight | under 2 s / under 20 s |
| Core RSS / llm RSS / total | at most 450 / 600 / 1200 MB |
| False critical alerts on `clean_21d` | 0; false advisory at most 1 per week |
| Store size, 21 days | warm under 400 MB, cold under 250 MB |
| Safety suite | all pass |
Report all gates in `bench/results/<date>.md`, including misses. Do not tune the golden set to the model; add questions, never delete failing ones.

## 4. Benchmark harness (`python -m bench.run`)
Starts the stack under Docker with `cpus: 2`, `mem_limit: 2g` (the `a55` profile), loads `demo_21d`, replays the golden set 5 times, records stage timings from SSE `done` events, samples RSS from cgroup files every second, and writes the report. Also runs 10 minutes of live ingest at 1x and reports dropped samples. Compare models with `--model` flag.

## 5. Integration tests (examples)
- Sim `fast_charge_overtemp` produces exactly one `battery_temp_high` event; black-box window has samples from T-60 s to T+60 s; evidence ranks fast charge first; template narration passes the verifier.
- `clean_21d` produces no warning or critical insights.
- Kill `llm` mid-ask: card and template answer still arrive; `verified=false`.
- Out-of-order and duplicated frames do not create duplicate events.
- Retention purge keeps black-box windows.

## 6. UI end to end (Playwright, also run by the browser agent)
Each state in `UX_SPEC.md` section 4; keyboard path; driving-mode collapse; no non-local network requests; screenshots saved to `bench/results/ui/`.

## 7. CI
GitHub Actions: lint, unit, integration, safety, web tests on every push. Nightly: model suite, benchmark (amd64), and an arm64 run under QEMU for functionality only (not timing). Cache uv and pnpm.
