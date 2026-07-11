package com.helpdesk.ticket.web.dto;

import java.time.Instant;

import com.helpdesk.ticket.domain.Ticket;
import com.helpdesk.ticket.domain.TicketPriority;
import com.helpdesk.ticket.domain.TicketStatus;

public record TicketResponse(
        Long id,
        String title,
        String description,
        TicketStatus status,
        TicketPriority priority,
        Long requesterId,
        Long assigneeId,
        Instant createdAt,
        Instant updatedAt,
        Instant slaDueAt) {

    public static TicketResponse from(Ticket ticket) {
        return new TicketResponse(
                ticket.getId(),
                ticket.getTitle(),
                ticket.getDescription(),
                ticket.getStatus(),
                ticket.getPriority(),
                ticket.getRequesterId(),
                ticket.getAssigneeId(),
                ticket.getCreatedAt(),
                ticket.getUpdatedAt(),
                ticket.getSlaDueAt());
    }
}
