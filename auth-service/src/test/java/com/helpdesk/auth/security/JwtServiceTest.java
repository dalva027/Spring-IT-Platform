package com.helpdesk.auth.security;

import java.util.Date;

import com.helpdesk.auth.user.Role;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class JwtServiceTest {

    private final JwtService jwtService = new JwtService("test-secret-test-secret-test-secret-42", 60);

    @Test
    void issuedTokenRoundTripsClaims() {
        String token = jwtService.issueToken(42L, "jane@example.com", Role.AGENT);

        Claims claims = jwtService.parse(token);

        assertThat(claims.getSubject()).isEqualTo("42");
        assertThat(claims.get("email", String.class)).isEqualTo("jane@example.com");
        assertThat(claims.get("role", String.class)).isEqualTo("AGENT");
        assertThat(claims.getExpiration()).isAfter(new Date());
    }

    @Test
    void parseRejectsTokenSignedWithDifferentKey() {
        JwtService other = new JwtService("another-secret-another-secret-another-42", 60);
        String token = other.issueToken(1L, "jane@example.com", Role.REQUESTER);

        assertThatThrownBy(() -> jwtService.parse(token)).isInstanceOf(JwtException.class);
    }
}
