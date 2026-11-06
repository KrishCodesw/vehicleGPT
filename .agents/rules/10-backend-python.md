# Backend Python rules (apply to `vgpt/**/*.py`)

- Python 3.12, type hints everywhere, mypy strict on `vgpt/`. ruff for lint and format. Line length 100.
- pydantic v2 models for all data crossing a module boundary. No dicts of unknown shape across boundaries.
- Interfaces are `typing.Protocol` classes in `base.py`; wire implementations in `vgpt/core/wiring.py` from `Settings`.
- asyncio first. Blocking or CPU-heavy work goes to the single worker pool, never the event loop. No `time.sleep`; use the clock abstraction in tests.
- SQLite: one writer task; read connections per request; bound parameters only; SQL lives in `.sql` files for tools; migrations are idempotent.
- Units: carry units in names (`_kw`, `_c`, `_bar`, `_ms`). Convert at the edges only.
- Determinism: seeded `numpy.random.Generator`; no global RNG; sort before hashing or comparing.
- Errors: raise typed exceptions from `vgpt.common.errors`; never swallow; log once at the boundary with context but no PII.
- Logging: structured JSON, levels used sensibly, no f-string interpolation of large objects.
- Performance: avoid per-sample Python loops in hot paths; batch with numpy; benchmark before optimising; keep core RSS inside the budget.
- Tests: pytest, one behaviour per test, table-driven where useful, hypothesis for verifier and unit conversion, fixtures build tiny stores in `tmp_path`. Mark model-dependent tests `@pytest.mark.model`.
- Dependencies: only the approved stack (FastAPI, uvicorn, pydantic, python-can, cantools, numpy, scipy, ruptures, httpx, fastembed, pytest, hypothesis, pytest-asyncio, pyyaml, sse-starlette, ruff, mypy; dev only: matplotlib, playwright). Ask before adding anything else.
- Docstrings state units, time base and failure behaviour for public functions.
