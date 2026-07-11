package com.helpdesk.auth.web.dto;

import java.time.Instant;

import com.helpdesk.auth.user.User;

public record UserResponse(Long id, String email, String fullName, String role, Instant createdAt) {

    public static UserResponse from(User user) {
        return new UserResponse(
                user.getId(),
                user.getEmail(),
                user.getFullName(),
                user.getRole().name(),
                user.getCreatedAt());
    }
}
