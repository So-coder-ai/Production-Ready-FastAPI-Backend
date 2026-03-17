# FastAPI backend (JWT + Postgres)

This is a small, clean backend you can use as a starting point for a real project.

## What you get
- FastAPI with a modular layout
- JWT signup/login
- Postgres + SQLAlchemy ORM
- Task CRUD (tasks belong to the logged-in user)
- Pydantic validation, correct status codes, and consistent errors
- JSON logs
- Pagination + simple filtering on task listing
- Swagger docs
- Docker + docker-compose

## Project structure
```
app/
  api/
    deps.py
    router.py
    routers/
      auth.py
      users.py
      tasks.py
  core/
    config.py
    logging.py
    security.py
  db/
    base.py
    session.py
  models/
    user.py
    task.py
  schemas/
    user.py
    token.py
    task.py
    pagination.py
  services/
    user_service.py
    task_service.py
  main.py
```

## Running with Docker (recommended)
Start Postgres + API:

```bash
docker compose up --build
```

Docs:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

## Running locally (without Docker)
Create a virtualenv and install deps:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and point `DATABASE_URL` at your Postgres.

Run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs: `http://localhost:8000/api/v1/docs`

## API overview

### Auth
- `POST /api/v1/auth/signup` (JSON body)

```json
{ "email": "user@example.com", "password": "strongpassword" }
```

- `POST /api/v1/auth/login` (form-data: `username`, `password`)

Response:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

### Current user
- `GET /api/v1/users/me` (Bearer token required)

### Tasks (Bearer token required)
- `POST /api/v1/tasks`
- `GET /api/v1/tasks?skip=0&limit=20&status=todo&q=search`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `DELETE /api/v1/tasks/{task_id}`

## Notes
- Alembic is included; use migrations for real deployments.
- Set a strong `JWT_SECRET_KEY`.
