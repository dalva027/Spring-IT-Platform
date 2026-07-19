FROM python:3.12-slim

WORKDIR /srv/ai-service

# Install dependencies first for layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

EXPOSE 8083

# Apply migrations, then serve. Migrations are idempotent (alembic version table).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8083"]
