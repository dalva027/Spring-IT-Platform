package com.helpdesk.auth.web.dto;

import com.helpdesk.auth.user.Role;
import jakarta.validation.constraints.NotNull;

public record RoleUpdateRequest(@NotNull Role role) {
}
