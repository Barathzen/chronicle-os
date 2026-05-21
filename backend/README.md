Chronicle OS — Backend (Docker) README
=====================================

Overview
--------
This document explains how to run the backend locally using Docker Compose in a professional, repeatable way. It assumes you want a development setup that mirrors production where possible: Postgres with `pgvector`, Redis, and the FastAPI backend.

Prerequisites
-------------
- Docker & Docker Compose (v2) installed and working
- Git (to clone/update repo)
- A copy of the repository checked out locally

Files of interest
-----------------
- `backend/Dockerfile` — backend image build
- `docker-compose.yml` — local compose stack (db, redis, backend)
- `backend/.env` or top-level `.env` — environment variables (never commit secrets)
- `backend/alembic/versions/...` — migrations (the pgvector conversion migration is guarded)

Quickstart — Development (Docker Compose)
----------------------------------------
1. Copy example env (if present) and edit values as needed:

```bash
cp backend/.env.example backend/.env  # if provided
# Edit `backend/.env` and set SECRET_KEY and other values
```

2. Build and start the stack (Postgres with `pgvector`, Redis, backend):

```bash
docker compose up --build -d
```

3. Run database migrations (inside the backend container):

```bash
docker compose exec backend alembic upgrade head
```

Note: The repository includes a guarded migration to create the `vector` extension and populate a new `embedding_vector` column only if the server supports `pgvector`. The compose stack uses an image with `pgvector` preinstalled; if you change the Postgres image you may need to install the extension manually.

4. Tail logs and confirm the backend is running:

```bash
docker compose logs -f backend
# open http://localhost:8000/docs for the FastAPI OpenAPI UI
```

Useful local commands
---------------------
- Stop and remove containers (keep volumes):

```bash
docker compose down
```

- Stop and remove containers and volumes (clean DB):

```bash
docker compose down -v
```

- Run tests inside the container (requires dependencies in image):

```bash
docker compose exec backend pytest -q
```

Environment variables (common)
------------------------------
- `DATABASE_URL` — e.g. `postgresql://postgres:postgres@db:5432/chronicle_os`
- `REDIS_URL` — e.g. `redis://redis:6379/0`
- `SECRET_KEY` — set a strong secret in development and production
- `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM` — auth settings

PGVector migration notes
------------------------
- The provided Alembic migration `2b3c4d5e6f7g_convert_embedding_to_vector.py` attempts to create the `vector` extension and add an `embedding_vector` column populated from existing JSON embeddings. It is intentionally guarded: if the extension cannot be created (missing support or permissions) the migration exits without making changes.
- When using the included `ankane/pgvector:postgres-16` image in `docker-compose.yml`, the extension should be available and the migration will populate the `embedding_vector` column. After verifying correctness you can add a migration to drop or rename the JSON column if desired.

Troubleshooting
---------------
- Port 5432 or 8000 already in use: stop the other services or change the ports in `docker-compose.yml`.
- If migrations fail with permission errors creating extensions, ensure the DB image supports `pgvector` or run migrations as a superuser in a disposable DB to create the extension.
- If you see stale state from previous runs, bring the stack down and remove volumes:

```bash
docker compose down -v
```

Production notes (brief)
-----------------------
- Use a production-ready process manager (Gunicorn + Uvicorn workers) rather than the simple `uvicorn` command used in development.
- Use managed Postgres in production (AWS RDS / Azure Database / GCP Cloud SQL) and enable pgvector extension where supported.
- Store secrets securely (Vault, environment variables in orchestrator, or cloud secret manager).
- Add healthchecks and readiness probes for orchestration.

Next steps I can help with
-------------------------
- Add a CI workflow that builds the Docker image and runs tests using the compose stack.
- Add a migration to safely drop/rename the JSON `embedding` column after conversion.
- Harden the `backend/Dockerfile` for smaller images and better caching.

CI (GitHub Actions)
--------------------
We include a CI workflow that runs tests on push and PRs. It starts a `pgvector`-enabled Postgres and Redis service, installs dependencies, runs Alembic migrations, and executes the test suite using the `dummy` embedder to avoid heavy model downloads.

To run the same steps locally (useful for debugging CI):

```bash
# from repository root
docker compose up -d
cd backend
alembic upgrade head
EMBEDDER_PROVIDER=dummy pytest -q
```

If you want CI to test the sentence-transformers path, we can modify the workflow to cache and preinstall the model, but that will significantly increase runtime.
