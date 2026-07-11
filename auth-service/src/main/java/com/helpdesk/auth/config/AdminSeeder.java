package com.helpdesk.auth.config;

import com.helpdesk.auth.user.Role;
import com.helpdesk.auth.user.User;
import com.helpdesk.auth.user.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Seeds a default admin account on startup so role management works out of the box.
 * Disable with app.seed-admin.enabled=false outside local development.
 */
@Component
public class AdminSeeder implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(AdminSeeder.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final boolean enabled;
    private final String email;
    private final String password;

    public AdminSeeder(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            @Value("${app.seed-admin.enabled:false}") boolean enabled,
            @Value("${app.seed-admin.email:admin@helpdesk.local}") String email,
            @Value("${app.seed-admin.password:ChangeMe123!}") String password) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.enabled = enabled;
        this.email = email;
        this.password = password;
    }

    @Override
    public void run(String... args) {
        if (!enabled || userRepository.existsByEmailIgnoreCase(email)) {
            return;
        }
        User admin = new User();
        admin.setEmail(email);
        admin.setPasswordHash(passwordEncoder.encode(password));
        admin.setFullName("Helpdesk Admin");
        admin.setRole(Role.ADMIN);
        userRepository.save(admin);
        log.info("Seeded default admin user '{}'", email);
    }
}
