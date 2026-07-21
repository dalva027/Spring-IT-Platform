CREATE TABLE messages (
    id           BIGSERIAL PRIMARY KEY,
    sender_id    BIGINT        NOT NULL,
    recipient_id BIGINT        NOT NULL,
    subject      VARCHAR(200)  NOT NULL,
    body         VARCHAR(5000) NOT NULL,
    ticket_id    BIGINT,
    parent_id    BIGINT        REFERENCES messages (id) ON DELETE SET NULL,
    root_id      BIGINT,
    is_read      BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ   NOT NULL,
    read_at      TIMESTAMPTZ
);

CREATE INDEX idx_messages_recipient_id ON messages (recipient_id);
CREATE INDEX idx_messages_sender_id ON messages (sender_id);
CREATE INDEX idx_messages_root_id ON messages (root_id);
-- Speeds up the unread badge count.
CREATE INDEX idx_messages_recipient_unread ON messages (recipient_id) WHERE is_read = FALSE;
