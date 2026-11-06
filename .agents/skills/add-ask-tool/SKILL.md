---
name: add-ask-tool
description: Add a new parameterised tool and intent to the ask engine (planner schema, SQL template, facts, router exemplars, golden questions). Use when the assistant must answer a new kind of vehicle question.
---
# Add an ask tool

1. Read `docs/AI_PIPELINE.md` sections 1 to 5 and 7.
2. Define the intent name (add to the `Intent` enum) and its plan fields; extend `QueryPlan` only if needed. Keep the planner output small.
3. Create `vgpt/ask/tools/<name>.py` implementing `AskTool`: `args_model` (pydantic), `run(args, store, clock) -> ToolResult`. Use SQL templates in `vgpt/ask/tools/sql/<name>.sql` with bound parameters only. No string-built SQL, no dynamic table names.
4. Return `facts` for every number or time a narration may quote (id, label, value, unit, kind, ts_ms). Add a `chart` spec (line or bar) and a short `table` if useful. Set `confidence` and `caveats`.
5. Router: add regex patterns and 8 to 10 exemplar phrasings for the intent in `vgpt/ask/router_data/<intent>.yaml`. Add a signal-synonym entry if new wording appears.
6. Template: add the narration template in `vgpt/ask/templates.py` filled only from facts.
7. Tests: unit-test the tool on a tiny store against hand-computed values; add at least 6 golden questions (paraphrases, a follow-up, a near-miss that must be `unsupported`) with expected facts from `ground_truth.json`.
8. Check latency: the tool must stay under 300 ms p95 on `demo_21d` in the `a55` container; if not, add a rollup-backed path.
9. Run `make test lint safety`, then `make bench`; update `docs/AI_PIPELINE.md` tool table in the same commit.
