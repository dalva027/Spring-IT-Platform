package com.helpdesk.auth.service;

import java.util.Locale;

import com.helpdesk.auth.exception.EmailAlreadyUsedException;
import com.helpdesk.auth.exception.InvalidCredentialsException;
import com.helpdesk.auth.security.JwtService;
import com.helpdesk.auth.user.Role;
import com.helpdesk.auth.user.User;
import com.helpdesk.auth.user.UserRepository;
import com.helpdesk.auth.web.dto.AuthResponse;
import com.helpdesk.auth.web.dto.LoginRequest;
import com.helpdesk.auth.web.dto.RegisterRequest;
import com.helpdesk.auth.web.dto.UserResponse;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmailIgnoreCase(request.email())) {
            throw new EmailAlreadyUsedException(request.email());
        }
        User user = new User();
        user.setEmail(request.email().toLowerCase(Locale.ROOT));
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setFullName(request.fullName());
        user.setRole(Role.REQUESTER);
        return toAuthResponse(userRepository.save(user));
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmailIgnoreCase(request.email())
                .orElseThrow(InvalidCredentialsException::new);
        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new InvalidCredentialsException();
        }
        return toAuthResponse(user);
    }

    private AuthResponse toAuthResponse(User user) {
        String token = jwtService.issueToken(user.getId(), user.getEmail(), user.getRole());
        return new AuthResponse(token, UserResponse.from(user));
    }
}
