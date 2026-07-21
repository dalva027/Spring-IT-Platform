package com.helpdesk.ticket.exception;

public class MessageNotFoundException extends RuntimeException {

    public MessageNotFoundException(Long id) {
        super("Message %d not found".formatted(id));
    }
}
