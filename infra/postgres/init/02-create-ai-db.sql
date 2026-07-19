-- ai-service owns its own database, like the other services.
-- NOTE: docker-entrypoint init scripts only run on a FRESH pgdata volume.
-- For an existing volume, run this once by hand:
--   docker exec -i helpdesk-postgres psql -U helpdesk -d auth_db -f /docker-entrypoint-initdb.d/02-create-ai-db.sql
CREATE DATABASE ai_db OWNER helpdesk;

\connect ai_db

CREATE EXTENSION IF NOT EXISTS vector;
