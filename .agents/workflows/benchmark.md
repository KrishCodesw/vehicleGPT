---
description: Run latency, memory, storage and golden-set benchmarks in the a55 container
---
1. Confirm M8 prerequisites exist (Compose profile `a55`, golden set, `bench/run.py`).
2. Start the stack with `VGPT_PROFILE=a55`, `cpus: 2`, `mem_limit: 2g`. Load `demo_21d`.
3. Run `make bench` (golden set 5 times, 10 minutes of live ingest at 1x).
4. Collect: answer-card, first-token and total latency p50 and p95 by stage; RSS for core and llm from cgroup files; dropped samples; verifier block rate; store size by tier; intent and evidence accuracy.
5. Write `bench/results/<date>.md` with a table of every gate in `docs/TEST_PLAN.md` section 3, marked pass or miss. Do not hide misses or tune the golden set.
6. If a gate is missed, list the likely cause and the cheapest fix (for example 0.5B model, fewer planner calls, smaller context, template-first narration) and ask the human before changing scope.
7. Compare models only with `--model` runs and report the table; never change the default model without the numbers.
