# API (FastAPI, base `/v1`)

Auth: `Authorization: Bearer <token>`; roles `driver`, `service` from `VGPT_TOKENS` (dev). Driver tokens cannot call `/cases` or `/export`. Errors: `{ "error": {"code": "...", "message": "..."} }`.

## REST
| Method and path | Role | Purpose |
|---|---|---|
| GET `/health` | any | `{status, model:"up|down", store:"ok", uptime_s}` |
| GET `/metrics` | any | RSS, stage latency p50/p95, ingest rate, dropped samples, queue depth, verifier block rate |
| GET `/vehicle/state` | any | `{ts_ms, mode:"driving|parked|charging", soc_pct, range_km, ambient_c, speed_kmh}` |
| GET `/insights?status=queued,delivered&limit=20` | any | list insights |
| POST `/insights/{id}/ack` and `/dismiss` | any | mark delivered or dismissed (dismiss feeds suppression) |
| GET `/events?type=&from=&to=&limit=` | any | events |
| GET `/events/{id}` | any | event with evidence pack and black-box availability |
| GET `/events/{id}/timeline?signals=a,b` | service | black-box series for charts |
| GET `/signals` | any | catalogue |
| GET `/signals/{name}/series?from=&to=&bucket=` | any | series (hour, day, 1m, raw) |
| GET `/cases/{event_id}` | service | auto case file (ranked causes, timeline refs, DTC text) |
| GET `/export/bundle?event_id=` | service | zip of case file JSON + CSV of window |
| GET `/store/size` | service | size report per tier |
| POST `/ask` | any | SSE, see below |
| POST `/sim/scenario` `{name,speed}` | dev only | control the simulator (disabled outside `dev`) |

## Insight object
```json
{ "id":"ins_01","kind":"EVENT_EXPLANATION","severity":"warning","subject":"battery_temp","title":"Battery heated up 11 °C in 8 minutes",
  "narration":"Pack temperature rose from 36 to 47 °C ...","narration_source":"template|model","verified":true,
  "evidence":{ "...EvidencePack..." }, "status":"queued","created_ms":0,"event_id":"evt_01" }
```

## POST /ask
Request `{ "text":"Why has my range dropped?", "insight_id": null, "lang":"en" }`. Response is `text/event-stream`:
- `event: route` data `{intent, path:"fast|planner", ms}`
- `event: card` data `{title, facts:[...], table?, chart?:{type:"line|bar", series:[...]}, confidence}`
- `event: token` data `{t:"..."}` (repeat)
- `event: verified` data `{ok:true|false, source:"model|template", text:"full final text"}`
- `event: done` data `{timings:{route,plan,tools,card,ttft,total}}`
- `event: error` data `{code, message}`
Clients render the card on `card`, stream tokens, and replace with `verified.text` when `source` is `template`.

## WebSocket `/stream` (token as query param)
Server pushes JSON: `{type:"vehicle.state", ...}`, `{type:"insight.created", insight}`, `{type:"insight.updated", insight}` (narration upgraded), `{type:"policy.hold", id, reason}`. Heartbeat every 15 s.

## Contract rules
Pydantic models in `vgpt/api/schemas.py` are the source of truth; generate `apps/web/lib/api-types.ts` from OpenAPI in CI and fail on drift. Breaking changes require an update to this file in the same commit.
