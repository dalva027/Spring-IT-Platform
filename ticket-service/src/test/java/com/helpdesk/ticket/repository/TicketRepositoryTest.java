package com.helpdesk.ticket.repository;

import java.time.Duration;
import java.time.Instant;
import java.util.EnumSet;
import java.util.List;

import com.helpdesk.ticket.domain.Ticket;
import com.helpdesk.ticket.domain.TicketPriority;
import com.helpdesk.ticket.domain.TicketStatus;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class TicketRepositoryTest {

    @Autowired
    private TicketRepository ticketRepository;

    @Test
    void findsOnlyActiveTicketsPastTheirSlaDeadline() {
        Instant now = Instant.now();
        saveTicket("Overdue open", TicketStatus.OPEN, now.minus(Duration.ofHours(3)));
        saveTicket("Overdue but resolved", TicketStatus.RESOLVED, now.minus(Duration.ofHours(3)));
        saveTicket("Still within SLA", TicketStatus.OPEN, now.plus(Duration.ofHours(3)));

        List<Ticket> breached = ticketRepository.findSlaBreached(
                now, EnumSet.of(TicketStatus.OPEN, TicketStatus.IN_PROGRESS));

        assertThat(breached).extracting(Ticket::getTitle).containsExactly("Overdue open");
    }

    @Test
    void aggregatesTicketCountsByStatus() {
        Instant due = Instant.now().plus(Duration.ofHours(24));
        saveTicket("First open", TicketStatus.OPEN, due);
        saveTicket("Second open", TicketStatus.OPEN, due);
        saveTicket("One resolved", TicketStatus.RESOLVED, due);

        List<TicketAgingView> rows = ticketRepository.aggregateAging();

        assertThat(rows).hasSize(2);
        TicketAgingView open = rows.stream()
                .filter(row -> row.getStatus() == TicketStatus.OPEN)
                .findFirst()
                .orElseThrow();
        assertThat(open.getTicketCount()).isEqualTo(2);
        assertThat(open.getOldestCreatedAt()).isNotNull();
    }

    private void saveTicket(String title, TicketStatus status, Instant slaDueAt) {
        Ticket ticket = new Ticket();
        ticket.setTitle(title);
        ticket.setDescription("Test ticket");
        ticket.setPriority(TicketPriority.MEDIUM);
        ticket.setStatus(status);
        ticket.setRequesterId(1L);
        ticket.setSlaDueAt(slaDueAt);
        ticketRepository.saveAndFlush(ticket);
    }
}
