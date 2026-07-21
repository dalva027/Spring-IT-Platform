package com.helpdesk.auth.web;

import java.util.List;

import com.helpdesk.auth.security.AuthenticatedUser;
import com.helpdesk.auth.user.User;
import com.helpdesk.auth.user.UserRepository;
import com.helpdesk.auth.web.dto.ContactResponse;
import com.helpdesk.auth.web.dto.RoleUpdateRequest;
import com.helpdesk.auth.web.dto.UserResponse;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/users")
public class UserController {

    /** Seeded non-interactive service account (V2 migration); never a messaging recipient. */
    private static final long AI_SERVICE_USER_ID = 9000L;

    private final UserRepository userRepository;

    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @GetMapping("/me")
    public UserResponse me(@AuthenticationPrincipal AuthenticatedUser principal) {
        return UserResponse.from(findUser(principal.id()));
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('AGENT', 'ADMIN')")
    public List<UserResponse> list() {
        return userRepository.findAll().stream().map(UserResponse::from).toList();
    }

    /**
     * Slim directory (id/name/role, no email) for the messaging recipient picker.
     * Available to any authenticated user; excludes the caller and the AI service account.
     */
    @GetMapping("/contacts")
    public List<ContactResponse> contacts(@AuthenticationPrincipal AuthenticatedUser principal) {
        return userRepository.findAll().stream()
                .filter(user -> !user.getId().equals(principal.id()))
                .filter(user -> !user.getId().equals(AI_SERVICE_USER_ID))
                .map(ContactResponse::from)
                .toList();
    }

    @PatchMapping("/{id}/role")
    @PreAuthorize("hasRole('ADMIN')")
    public UserResponse updateRole(@PathVariable Long id, @Valid @RequestBody RoleUpdateRequest request) {
        User user = findUser(id);
        user.setRole(request.role());
        return UserResponse.from(userRepository.save(user));
    }

    private User findUser(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "User %d not found".formatted(id)));
    }
}
