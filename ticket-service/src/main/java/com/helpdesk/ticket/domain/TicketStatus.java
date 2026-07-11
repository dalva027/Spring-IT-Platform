package com.helpdesk.ticket.domain;

import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

public enum TicketStatus {
    OPEN,
    IN_PROGRESS,
    RESOLVED,
    CLOSED;

    private static final Map<TicketStatus, Set<TicketStatus>> ALLOWED_TRANSITIONS = Map.of(
            OPEN, EnumSet.of(IN_PROGRESS, CLOSED),
            IN_PROGRESS, EnumSet.of(OPEN, RESOLVED),
            RESOLVED, EnumSet.of(OPEN, CLOSED),
            CLOSED, EnumSet.noneOf(TicketStatus.class));

    public boolean canTransitionTo(TicketStatus target) {
        return ALLOWED_TRANSITIONS.get(this).contains(target);
    }
}
