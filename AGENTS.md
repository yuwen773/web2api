# Repository Guidelines

## Project Structure & Module Organization
This repository is currently scaffolded for a Python web-to-API bridge.

- `src/api/`: provider-compatible HTTP routes (planned: OpenAI/Anthropic endpoints).
- `src/client/`: upstream platform client logic (auth, sessions, chat streaming).
- `src/models/`: Pydantic request/response models.
- `src/utils/`: shared helpers (SSE parsing, token counting, retries).
- `tests/`: unit and integration tests.
- `config/`: runtime config templates (do not commit secrets).
- `docs/`: technical assessments and implementation plans.
- `crawler/`: captured request/response samples used for reverse-engineering.
- `memory-bank/`: working notes and intermediate design records.

## Build, Test, and Development Commands
Use these commands as the baseline workflow:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pytest -q
```

Useful targeted run:

```bash
pytest tests/test_login.py -k login -q
```

If Docker files are added per plan:

```bash
docker compose up --build -d
```

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and explicit type hints on public functions.
- Use `snake_case` for modules/functions, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- Keep API route files provider-focused (for example, `src/api/openai.py`).
- Keep functions small and side effects isolated in `src/client/` and `src/utils/`.

## Testing Guidelines
- Use `pytest` and `pytest-asyncio` for async flows.
- Name tests as `tests/test_<feature>.py`; test functions should describe behavior clearly.
- Mock external HTTP calls where possible; gate real-network tests behind explicit markers.
- For new logic, include happy path, error path, and streaming/SSE edge-case coverage.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (observed in history): `feat: ...`, `fix: ...`, `docs: ...`.
- Keep commits focused and explain behavior changes, not only file changes.
- PRs should include: summary, key changed paths, test evidence (`pytest` output), and linked issue/task.
- For API changes, include sample request/response (curl or JSON snippets).

## Security & Configuration Tips
- Never commit credentials, JWTs, or session cookies from `crawler/` artifacts.
- Keep secrets in `.env` (already gitignored) and commit only sanitized config templates.
- Before pushing, review captured payload files for sensitive user/account data.
