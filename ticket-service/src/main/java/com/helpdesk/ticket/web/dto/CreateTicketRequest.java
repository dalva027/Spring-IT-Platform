package com.helpdesk.ticket.web.dto;

import com.helpdesk.ticket.domain.TicketPriority;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CreateTicketRequest(
        @NotBlank @Size(max = 200) String title,
        @NotBlank @Size(max = 10000) String description,
        @NotNull TicketPriority priority) {
}
