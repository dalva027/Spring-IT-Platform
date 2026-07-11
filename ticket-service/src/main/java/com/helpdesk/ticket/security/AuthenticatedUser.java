package com.helpdesk.ticket.security;

/**
 * Principal extracted from a JWT issued by the auth-service.
 * The token is trusted via the shared signing secret; no user lookup is needed here.
 */
public record AuthenticatedUser(Long id, String email, String role) {

    public boolean isRequester() {
        return "REQUESTER".equals(role);
    }
}
