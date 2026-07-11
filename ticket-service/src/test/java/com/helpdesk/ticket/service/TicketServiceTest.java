package com.helpdesk.ticket.service;

import java.time.Duration;
import java.time.Instant;
import java.util.Optional;

import com.helpdesk.ticket.domain.StatusHistory;
import com.helpdesk.ticket.domain.Ticket;
import com.helpdesk.ticket.domain.TicketPriority;
import com.helpdesk.ticket.domain.TicketStatus;
import com.helpdesk.ticket.exception.InvalidStatusTransitionException;
import com.helpdesk.ticket.exception.TicketNotFoundException;
import com.helpdesk.ticket.repository.CommentRepository;
import com.helpdesk.ticket.repository.StatusHistoryRepository;
import com.helpdesk.ticket.repository.TicketRepository;
import com.helpdesk.ticket.security.AuthenticatedUser;
import com.helpdesk.ticket.web.dto.CreateTicketRequest;
import com.helpdesk.ticket.web.dto.TicketResponse;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.access.AccessDeniedException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TicketServiceTest {

    @Mock
    private TicketRepository ticketRepository;

    @Mock
    private CommentRepository commentRepository;

    @Mock
    private StatusHistoryRepository statusHistoryRepository;

    @InjectMocks
    private TicketService ticketService;

    private final AuthenticatedUser requester = new AuthenticatedUser(1L, "jane@example.com", "REQUESTER");
    private final AuthenticatedUser agent = new AuthenticatedUser(2L, "agent@example.com", "AGENT");

    @Test
    void createSetsSlaDeadlineFromPriorityAndRecordsHistory() {
        when(ticketRepository.save(any(Ticket.class))).thenAnswer(invocation -> invocation.getArgument(0));
        Instant before = Instant.now();

        TicketResponse response = ticketService.create(
                new CreateTicketRequest("VPN down", "Cannot connect to the VPN", TicketPriority.CRITICAL), requester);

        assertThat(response.status()).isEqualTo(TicketStatus.OPEN);
        assertThat(response.requesterId()).isEqualTo(1L);
        assertThat(response.slaDueAt()).isAfterOrEqualTo(before.plus(Duration.ofHours(2)));
        assertThat(response.slaDueAt()).isBeforeOrEqualTo(Instant.now().plus(Duration.ofHours(2)));

        ArgumentCaptor<StatusHistory> captor = ArgumentCaptor.forClass(StatusHistory.class);
        verify(statusHistoryRepository).save(captor.capture());
        assertThat(captor.getValue().getFromStatus()).isNull();
        assertThat(captor.getValue().getToStatus()).isEqualTo(TicketStatus.OPEN);
    }

    @Test
    void rejectsInvalidStatusTransition() {
        when(ticketRepository.findById(10L)).thenReturn(Optional.of(ticketWithStatus(TicketStatus.OPEN)));

        assertThatThrownBy(() -> ticketService.updateStatus(10L, TicketStatus.RESOLVED, agent))
                .isInstanceOf(InvalidStatusTransitionException.class);

        verify(statusHistoryRepository, never()).save(any());
    }

    @Test
    void recordsHistoryOnValidStatusTransition() {
        when(ticketRepository.findById(10L)).thenReturn(Optional.of(ticketWithStatus(TicketStatus.OPEN)));
        when(ticketRepository.save(any(Ticket.class))).thenAnswer(invocation -> invocation.getArgument(0));

        TicketResponse response = ticketService.updateStatus(10L, TicketStatus.IN_PROGRESS, agent);

        assertThat(response.status()).isEqualTo(TicketStatus.IN_PROGRESS);
        ArgumentCaptor<StatusHistory> captor = ArgumentCaptor.forClass(StatusHistory.class);
        verify(statusHistoryRepository).save(captor.capture());
        assertThat(captor.getValue().getFromStatus()).isEqualTo(TicketStatus.OPEN);
        assertThat(captor.getValue().getToStatus()).isEqualTo(TicketStatus.IN_PROGRESS);
        assertThat(captor.getValue().getChangedBy()).isEqualTo(2L);
    }

    @Test
    void requesterCannotReadSomeoneElsesTicket() {
        Ticket ticket = ticketWithStatus(TicketStatus.OPEN);
        ticket.setRequesterId(99L);
        when(ticketRepository.findById(10L)).thenReturn(Optional.of(ticket));

        assertThatThrownBy(() -> ticketService.get(10L, requester))
                .isInstanceOf(AccessDeniedException.class);
    }

    @Test
    void agentCanReadAnyTicket() {
        Ticket ticket = ticketWithStatus(TicketStatus.OPEN);
        ticket.setRequesterId(99L);
        when(ticketRepository.findById(10L)).thenReturn(Optional.of(ticket));

        assertThat(ticketService.get(10L, agent).requesterId()).isEqualTo(99L);
    }

    @Test
    void unknownTicketThrowsNotFound() {
        when(ticketRepository.findById(10L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> ticketService.get(10L, agent))
                .isInstanceOf(TicketNotFoundException.class);
    }

    private Ticket ticketWithStatus(TicketStatus status) {
        Ticket ticket = new Ticket();
        ticket.setTitle("Printer jam");
        ticket.setDescription("Paper stuck in tray 2");
        ticket.setPriority(TicketPriority.MEDIUM);
        ticket.setStatus(status);
        ticket.setRequesterId(1L);
        ticket.setSlaDueAt(Instant.now().plus(Duration.ofHours(24)));
        return ticket;
    }
}
