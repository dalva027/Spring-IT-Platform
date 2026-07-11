package com.helpdesk.ticket.web.dto;

import com.helpdesk.ticket.domain.TicketStatus;
import jakarta.validation.constraints.NotNull;

public record StatusUpdateRequest(@NotNull TicketStatus status) {
}
