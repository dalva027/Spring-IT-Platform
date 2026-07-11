package com.helpdesk.ticket.web.dto;

import java.time.Instant;

import com.helpdesk.ticket.domain.StatusHistory;
import com.helpdesk.ticket.domain.TicketStatus;

public record StatusHistoryResponse(
        Long id,
        TicketStatus fromStatus,
        TicketStatus toStatus,
        Long changedBy,
        Instant changedAt) {

    public static StatusHistoryResponse from(StatusHistory history) {
        return new StatusHistoryResponse(
                history.getId(),
                history.getFromStatus(),
                history.getToStatus(),
                history.getChangedBy(),
                history.getChangedAt());
    }
}
