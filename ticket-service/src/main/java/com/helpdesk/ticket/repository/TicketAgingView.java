package com.helpdesk.ticket.repository;

import java.time.Instant;

import com.helpdesk.ticket.domain.TicketStatus;

/**
 * Projection for the per-status aging aggregate query.
 */
public interface TicketAgingView {

    TicketStatus getStatus();

    long getTicketCount();

    Instant getOldestCreatedAt();
}
