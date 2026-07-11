package com.helpdesk.ticket.web.dto;

import com.helpdesk.ticket.domain.TicketStatus;

public record AgingReportRow(TicketStatus status, long ticketCount, long oldestAgeHours) {
}
