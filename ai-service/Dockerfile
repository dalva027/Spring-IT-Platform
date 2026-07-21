FROM python:3.12-slim

WORKDIR /srv/ai-service

# app/ is copied in as loose source (not pip-installed, since it doesn't exist
# yet when deps are installed below), so put the WORKDIR on the import path so
# `alembic` — which, unlike uvicorn, doesn't add CWD to sys.path — can import it.
ENV PYTHONPATH=/srv/ai-service

# Install dependencies first for layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

EXPOSE 8083

# Apply migrations, then serve. Migrations are idempotent (alembic version table).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8083"]
