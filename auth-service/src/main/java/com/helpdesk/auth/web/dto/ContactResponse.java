package com.helpdesk.auth.web.dto;

import com.helpdesk.auth.user.User;

/**
 * Minimal user directory entry for the messaging recipient picker. Unlike {@link UserResponse}
 * this omits email, so it is safe to expose to any authenticated user (not just agents).
 */
public record ContactResponse(Long id, String fullName, String role) {

    public static ContactResponse from(User user) {
        return new ContactResponse(user.getId(), user.getFullName(), user.getRole().name());
    }
}
