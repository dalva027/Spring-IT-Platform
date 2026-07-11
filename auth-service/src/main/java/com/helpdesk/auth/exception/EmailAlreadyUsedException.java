package com.helpdesk.auth.exception;

public class EmailAlreadyUsedException extends RuntimeException {

    public EmailAlreadyUsedException(String email) {
        super("Email is already registered: " + email);
    }
}
