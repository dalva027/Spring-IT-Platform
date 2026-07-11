package com.helpdesk.ticket.domain;

import java.time.Duration;

public enum TicketPriority {
    LOW(72),
    MEDIUM(24),
    HIGH(8),
    CRITICAL(2);

    private final int slaHours;

    TicketPriority(int slaHours) {
        this.slaHours = slaHours;
    }

    public Duration slaWindow() {
        return Duration.ofHours(slaHours);
    }
}
