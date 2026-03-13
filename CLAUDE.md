# Judge API — CLAUDE.md

A FastAPI backend for programming competition evaluation. Accepts code submissions in 8 languages, executes them in a sandboxed environment against test cases, and returns a verdict.

## Commands

```bash
# Install dependencies
poetry install

# Run API (port 8000)
make run
# or: hypercorn src.main:app --reload

# Lint
make lint
# or: blue .

# Run all tests
poetry run pytest

# Run a single test
poetry run pytest tests/unit/test_unit_submissions.py::test_create_submission -v

# Start full stack (API + MongoDB + Redis + worker)
docker-compose up -d --build

# Run migrations (upgrade)
mongodb-migrate \
  --url 'mongodb://127.0.0.1:27017/judge?replicaSet=rs0' \
  --migrations migrations \
  --database judge

# Run migrations (downgrade)
mongodb-migrate --downgrade \
  --url 'mongodb://127.0.0.1:27017/judge?replicaSet=rs0' \
  --migrations migrations \
  --database judge
```

## Architecture

Layered architecture: **controller → usecase → repository**

- **Controller** (`**/controller.py`): HTTP endpoints, Pydantic validation, dependency injection
- **UseCase** (`**/usecases.py`): business logic, transaction handling, queue enqueuing
- **Repository** (`src/contrib/repository/`): MongoDB abstraction via Motor (async)
- **Model** (`**/models.py`): database entity definitions (extend `BaseModelMixin`)
- **Schema** (`**/schemas.py`): request/response Pydantic models
- **Contrib** (`src/contrib/`): shared infrastructure — security, queue, judge engine, middleware

**Stack:** FastAPI + Hypercorn (ASGI), MongoDB + Motor, Redis + RQ, PyJWT, Pydantic v2

## Module Structure

```
src/
├── main.py                  # entrypoint (Hypercorn)
├── app.py                   # FastAPI factory, middleware, DB lifecycle
├── routers.py               # registers all routers
├── config.py                # env config (Pydantic Settings)
├── worker.py                # Redis RQ worker process
├── authentication/          # integrator JWT auth
├── submissions/             # code submission CRUD + judging trigger
├── problems/                # problem & test case CRUD
├── users/                   # user management
├── healthchecks/            # GET /healthchecks liveness probe
└── contrib/
    ├── judge.py             # judge engine + 8 language runners
    ├── queue.py             # QueueManager (Redis RQ singleton)
    ├── security.py          # JWT generation & validation
    ├── constants.py         # status codes, supported languages
    ├── repository/          # MongoDB base classes, connection
    ├── middleware/audit.py  # request audit logging
    └── models/base.py       # BaseModelMixin (id, created_at)
```

## Submission Lifecycle

1. `POST /v0/submissions` with `{ problem_id, language_type, content (base64) }`
2. JWT validated → `create:submissions` permission required
3. UseCase fetches problem, validates language + base64 content
4. `SubmissionModel` created with `status=PENDING`, persisted to MongoDB in a transaction
5. Job enqueued to Redis (`submissions` queue) with submission + problem data
6. Worker (`src/worker.py`) picks up job → calls `Judge.process_submission()`
7. Judge decodes code, selects language runner, executes against each test case with a 30s timeout
8. Each test case result is evaluated; worst status wins
9. Final status written back to MongoDB
10. Client polls `GET /v0/submissions/{id}` for the verdict

**Verdict statuses** (worst to best): `SECURITY_ERROR`, `COMPILATION_ERROR`, `RUNTIME_ERROR`, `TIME_LIMIT_EXCEEDED`, `MEMORY_LIMIT_EXCEEDED`, `WRONG_ANSWER`, `PRESENTATION_ERROR`, `ACCEPTED`

**Supported languages:** `py`, `c`, `cpp`, `java`, `js`, `php`, `go`, `cs`

## Authentication

Two-step JWT flow:

1. **Get token:** `POST /auth/integrator-token` with `{ "api_key": "<API_KEY_MASTER>" }`
2. **Use token:** `Authorization: Bearer <token>` on all protected endpoints

Tokens are HS256 JWTs signed with `API_KEY_MASTER` (env var), valid for 24 hours. The JWT payload carries `sub` (integrator ID) and `permissions`.

**Permission enum** (defined in `src/authentication/permissions.py`):
`read/create/update/delete` × `problems/submissions`

Endpoint guards use `Depends(validar_jwt_integrador([Permissions.X.value]))` from `src/contrib/security.py`.

The default integrator (seeded by migration) uses `API_KEY_MASTER` as its `hashed_api_key`.
