package com.helpdesk.ticket.exception;

import com.helpdesk.ticket.domain.TicketStatus;

public class InvalidStatusTransitionException extends RuntimeException {

    public InvalidStatusTransitionException(TicketStatus from, TicketStatus to) {
        super("Cannot transition ticket from %s to %s".formatted(from, to));
    }
}
