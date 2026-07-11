package com.helpdesk.auth.security;

/**
 * Lightweight principal extracted from a verified JWT.
 */
public record AuthenticatedUser(Long id, String email, String role) {
}
