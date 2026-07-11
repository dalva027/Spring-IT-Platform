package com.helpdesk.ticket.web.dto;

import jakarta.validation.constraints.NotNull;

public record AssigneeUpdateRequest(@NotNull Long assigneeId) {
}
