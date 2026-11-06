# AI pipeline

Principle: code finds and measures; the model plans a query and explains verified evidence. The model never reads raw telemetry, never writes SQL, never does arithmetic.

## 1. Intents (closed set)
`trend_explain`, `changepoint`, `event_list`, `pre_event_scan`, `compare_segments`, `trip_summary`, `point_lookup`, `insight_why`, `unsupported`.

## 2. Router (fast path, no LLM)
1. Normalise text. 2. Rule patterns (regex/keywords) per intent. 3. If ambiguous, cosine similarity to ~10 exemplars per intent using a small ONNX embedding model (MiniLM-class, int8, loaded lazily; `fastembed`). 4. Accept if score at least 0.55 and margin at least 0.08 over the runner-up; otherwise call the planner. Target router time under 60 ms.
Slot extraction for the fast path is rule-based (time phrases, signal synonyms from the catalogue, "city/highway", "yesterday", "last N weeks").

## 3. Planner (SLM, grammar-constrained)
Input: question, vehicle state summary (one line), signal catalogue names with synonyms (about 250 tokens, prefix-cached), optional `insight_id` context. Output: JSON `QueryPlan` enforced with llama.cpp `json_schema` or GBNF. Temperature 0, seed fixed, max 80 tokens.
```python
class TimeSpec(BaseModel):
    kind: Literal["last","day","between","since_event","all"]
    n: int | None = None; unit: Literal["hour","day","week"] | None = None
    day: Literal["today","yesterday"] | None = None
    start_iso: str | None = None; end_iso: str | None = None; event_id: str | None = None
class QueryPlan(BaseModel):
    intent: Intent
    metric: str | None = None             # catalogue signal or derived metric name
    signals: list[str] = []               # catalogue names only
    time: TimeSpec
    event_type: str | None = None         # e.g. adas_disengaged, battery_temp_high
    compare: dict[str,str] | None = None  # {"a":"city","b":"highway"}
    top_k: int = 5
```
Validation: unknown signals or metrics rejected (one constrained retry, then `unsupported`). Dates are resolved by `resolve_time(TimeSpec, clock)`; the model never computes dates.

## 4. Tools (parameterised; each returns `ToolResult(facts, table, chart, refs)`)
| Tool | Intent | Method |
|---|---|---|
| `trend` | trend_explain, point_lookup | bucketed series (hour/day) from warm or cold; slope and change vs previous window |
| `driver_decomposition` | trend_explain | regress daily efficiency (Wh/km) on ambient temp, HVAC power, mean speed, high-speed share, tyre pressure deficit; contribution of each factor = coefficient x change in factor between the two windows; report normalised shares and R2. If R2 under 0.5 say "low confidence". |
| `changepoint` | changepoint | PELT (ruptures) or CUSUM on daily series; return day, before/after means, size; pick largest drop |
| `events` | event_list | SQL on `event` by type, window; include reason codes and location geohash |
| `pre_event_scan` | pre_event_scan | black-box window; per signal compare last 10 min before T with the 14-day baseline for the same state; rank by absolute robust z and by rate of change; return top_k with values, baseline and z |
| `compare_segments` | compare_segments | segment by `road_type` (city vs highway), compute Wh/km, mean speed, HVAC share for each; report difference |
| `trip_summary` | trip_summary | from `trip` table |
Every tool returns `facts`: a list of `{id, label, value, unit, kind, ts_ms?}` that narration may quote. Tools use SQL templates in `vgpt/ask/tools/sql/*.sql` with bound parameters only.

## 5. Evidence pack
```python
class Fact(BaseModel): id: str; label: str; value: float | str; unit: str | None; kind: Literal["number","time","text"]; ts_ms: int | None = None
class Contributor(BaseModel): signal: str; label: str; value: float; unit: str; baseline: float; z: float; rank: int
class EvidencePack(BaseModel):
    kind: str; title_facts: list[str]; window: dict[str,int]; facts: list[Fact]
    contributors: list[Contributor] = []; chart: dict | None = None; refs: list[dict] = []   # refs: {signal, from_ms, to_ms}
    confidence: Literal["high","medium","low"]; caveats: list[str] = []
```
The same pack drives proactive insights and ask answers, so alerts and answers cannot disagree.

## 6. Narrator
Prompt skeleton (fixed, in `vgpt/ask/prompts/narrate.txt`): role is a vehicle assistant; use only the FACTS block; at most 3 sentences and 60 words; plain language; say "contributing factors" never "caused by" unless confidence is high; no instructions to the driver; if confidence is low say so. Inputs in a fenced `<facts>` block. Log text, if included, goes inside `<data>` fences, truncated to 200 characters, and the prompt states it is untrusted. Max 90 new tokens, temperature 0.2.
Templates: one per insight kind and intent in `vgpt/insight/narrate_templates.py`, filled only from facts. They are the fallback and the first narration for every event.

## 7. Verifier
Algorithm: extract numbers and times from the narration (regex covering `11 °C`, `11°C`, `11 degrees`, `47.2`, `4%`, `14:32`, `8 min`). Normalise units. Each extracted value must equal some fact within max(0.5 of the last shown digit, 1%). Times must match fact times within 1 minute. Ordinals and counts (for example "three events") must equal a fact. Any unmatched value fails. On fail: regenerate once with the instruction "use only these exact values"; fail again: use the template and set `verified=false`.
Property tests: any template output passes; injecting a perturbed number fails; unit variants normalise equally.

## 8. Model selection
| Profile | Model | File size | Why |
|---|---|---|---|
| `a55` | Qwen2.5-0.5B-Instruct Q4_K_M | about 0.4 GB | fits 2 GB with headroom; Apache-2.0 |
| `dev` | Qwen2.5-1.5B-Instruct Q4_K_M | about 1.1 GB | better wording and planning |
| alt | Llama-3.2-1B-Instruct Q4_K_M | about 0.8 GB | comparison baseline |
Evaluate each on the golden set (plan accuracy, narration pass rate, latency). Record results in `bench/results/`. Do not swap models without the numbers.
Optional LoRA (M9): train on synthetic question to QueryPlan pairs generated from the catalogue and scenarios (`bench/synth_plans.py`).

## 9. Latency budget (p95, `a55`)
Route 60 ms; plan 600 ms (only when needed); tools 300 ms; card 100 ms (card at under 1 s); narration first token under 2 s using prefix cache and max 90 tokens. Report every stage in metrics.

## 10. Unsupported and safety
Out-of-scope or non-vehicle questions: intent `unsupported`, answer "I can't answer that from vehicle data." with two example questions. Questions asking to control the vehicle or disable warnings: refuse and state that the assistant is read-only.
