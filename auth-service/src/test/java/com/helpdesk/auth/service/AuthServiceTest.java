package com.helpdesk.auth.service;

import java.util.Optional;

import com.helpdesk.auth.exception.EmailAlreadyUsedException;
import com.helpdesk.auth.exception.InvalidCredentialsException;
import com.helpdesk.auth.security.JwtService;
import com.helpdesk.auth.user.Role;
import com.helpdesk.auth.user.User;
import com.helpdesk.auth.user.UserRepository;
import com.helpdesk.auth.web.dto.AuthResponse;
import com.helpdesk.auth.web.dto.LoginRequest;
import com.helpdesk.auth.web.dto.RegisterRequest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtService jwtService;

    @InjectMocks
    private AuthService authService;

    @Test
    void registerCreatesRequesterWithEncodedPasswordAndLowercasedEmail() {
        RegisterRequest request = new RegisterRequest("Jane@Example.com", "s3cretPass!", "Jane Doe");
        when(userRepository.existsByEmailIgnoreCase("Jane@Example.com")).thenReturn(false);
        when(passwordEncoder.encode("s3cretPass!")).thenReturn("encoded-hash");
        ArgumentCaptor<User> captor = ArgumentCaptor.forClass(User.class);
        when(userRepository.save(captor.capture())).thenAnswer(invocation -> invocation.getArgument(0));
        when(jwtService.issueToken(any(), anyString(), any())).thenReturn("jwt-token");

        AuthResponse response = authService.register(request);

        User saved = captor.getValue();
        assertThat(saved.getEmail()).isEqualTo("jane@example.com");
        assertThat(saved.getPasswordHash()).isEqualTo("encoded-hash");
        assertThat(saved.getRole()).isEqualTo(Role.REQUESTER);
        assertThat(response.token()).isEqualTo("jwt-token");
        assertThat(response.user().fullName()).isEqualTo("Jane Doe");
    }

    @Test
    void registerRejectsDuplicateEmail() {
        when(userRepository.existsByEmailIgnoreCase("jane@example.com")).thenReturn(true);

        assertThatThrownBy(() -> authService.register(
                new RegisterRequest("jane@example.com", "s3cretPass!", "Jane Doe")))
                .isInstanceOf(EmailAlreadyUsedException.class);

        verify(userRepository, never()).save(any());
    }

    @Test
    void loginReturnsTokenForValidCredentials() {
        User user = existingUser();
        when(userRepository.findByEmailIgnoreCase("jane@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("s3cretPass!", "encoded-hash")).thenReturn(true);
        when(jwtService.issueToken(any(), anyString(), any())).thenReturn("jwt-token");

        AuthResponse response = authService.login(new LoginRequest("jane@example.com", "s3cretPass!"));

        assertThat(response.token()).isEqualTo("jwt-token");
        assertThat(response.user().email()).isEqualTo("jane@example.com");
    }

    @Test
    void loginRejectsWrongPassword() {
        when(userRepository.findByEmailIgnoreCase("jane@example.com")).thenReturn(Optional.of(existingUser()));
        when(passwordEncoder.matches("wrong-password", "encoded-hash")).thenReturn(false);

        assertThatThrownBy(() -> authService.login(new LoginRequest("jane@example.com", "wrong-password")))
                .isInstanceOf(InvalidCredentialsException.class);
    }

    @Test
    void loginRejectsUnknownEmail() {
        when(userRepository.findByEmailIgnoreCase("ghost@example.com")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> authService.login(new LoginRequest("ghost@example.com", "whatever!")))
                .isInstanceOf(InvalidCredentialsException.class);
    }

    private User existingUser() {
        User user = new User();
        user.setEmail("jane@example.com");
        user.setPasswordHash("encoded-hash");
        user.setFullName("Jane Doe");
        user.setRole(Role.REQUESTER);
        return user;
    }
}
