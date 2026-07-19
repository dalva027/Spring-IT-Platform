-- Service identity for ai-service. It mints its own HS256 JWTs with sub=9000,
-- so ticket-service resolves comments/assignments to a real user row.
-- The password hash is intentionally not a valid bcrypt hash: this account can
-- never log in through auth-service.
-- The fixed id 9000 is far above organic BIGSERIAL ids and does not advance the
-- sequence, so normal registrations keep getting small ids.
INSERT INTO users (id, email, password_hash, full_name, role, created_at)
VALUES (9000, 'ai@helpdesk.local', '!no-login-service-account', 'AI Assistant', 'AGENT', now())
ON CONFLICT (id) DO NOTHING;
