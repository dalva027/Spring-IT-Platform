CREATE TABLE tickets (
    id           BIGSERIAL PRIMARY KEY,
    title        VARCHAR(200)   NOT NULL,
    description  VARCHAR(10000) NOT NULL,
    status       VARCHAR(32)    NOT NULL,
    priority     VARCHAR(32)    NOT NULL,
    requester_id BIGINT         NOT NULL,
    assignee_id  BIGINT,
    created_at   TIMESTAMPTZ    NOT NULL,
    updated_at   TIMESTAMPTZ    NOT NULL,
    sla_due_at   TIMESTAMPTZ    NOT NULL
);

CREATE TABLE comments (
    id         BIGSERIAL PRIMARY KEY,
    ticket_id  BIGINT        NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    author_id  BIGINT        NOT NULL,
    body       VARCHAR(5000) NOT NULL,
    created_at TIMESTAMPTZ   NOT NULL
);

CREATE TABLE status_history (
    id          BIGSERIAL PRIMARY KEY,
    ticket_id   BIGINT      NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    from_status VARCHAR(32),
    to_status   VARCHAR(32) NOT NULL,
    changed_by  BIGINT      NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_tickets_status ON tickets (status);
CREATE INDEX idx_tickets_requester_id ON tickets (requester_id);
CREATE INDEX idx_tickets_assignee_id ON tickets (assignee_id);
CREATE INDEX idx_tickets_sla_due_at ON tickets (sla_due_at);
CREATE INDEX idx_comments_ticket_id ON comments (ticket_id);
CREATE INDEX idx_status_history_ticket_id ON status_history (ticket_id);
