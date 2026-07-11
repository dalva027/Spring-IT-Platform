package com.helpdesk.auth.web.dto;

public record AuthResponse(String token, UserResponse user) {
}
