package com.helpdesk.auth.user;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void findsUserByEmailIgnoringCase() {
        User user = new User();
        user.setEmail("jane@example.com");
        user.setPasswordHash("hash");
        user.setFullName("Jane Doe");
        user.setRole(Role.REQUESTER);
        userRepository.save(user);

        assertThat(userRepository.findByEmailIgnoreCase("JANE@EXAMPLE.COM")).isPresent();
        assertThat(userRepository.existsByEmailIgnoreCase("jane@example.com")).isTrue();
        assertThat(userRepository.findByEmailIgnoreCase("other@example.com")).isEmpty();
    }

    @Test
    void setsCreationTimestampOnPersist() {
        User user = new User();
        user.setEmail("tim@example.com");
        user.setPasswordHash("hash");
        user.setFullName("Tim Roe");
        user.setRole(Role.AGENT);

        User saved = userRepository.saveAndFlush(user);

        assertThat(saved.getId()).isNotNull();
        assertThat(saved.getCreatedAt()).isNotNull();
    }
}
