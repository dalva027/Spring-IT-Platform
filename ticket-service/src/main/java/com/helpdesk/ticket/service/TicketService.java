package com.helpdesk.ticket.service;

import java.time.Duration;
import java.time.Instant;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;

import com.helpdesk.ticket.domain.Comment;
import com.helpdesk.ticket.domain.StatusHistory;
import com.helpdesk.ticket.domain.Ticket;
import com.helpdesk.ticket.domain.TicketPriority;
import com.helpdesk.ticket.domain.TicketStatus;
import com.helpdesk.ticket.exception.InvalidStatusTransitionException;
import com.helpdesk.ticket.exception.TicketNotFoundException;
import com.helpdesk.ticket.repository.CommentRepository;
import com.helpdesk.ticket.repository.StatusHistoryRepository;
import com.helpdesk.ticket.repository.TicketRepository;
import com.helpdesk.ticket.repository.TicketSpecifications;
import com.helpdesk.ticket.security.AuthenticatedUser;
import com.helpdesk.ticket.web.dto.AgingReportRow;
import com.helpdesk.ticket.web.dto.CommentRequest;
import com.helpdesk.ticket.web.dto.CommentResponse;
import com.helpdesk.ticket.web.dto.CreateTicketRequest;
import com.helpdesk.ticket.web.dto.StatusHistoryResponse;
import com.helpdesk.ticket.web.dto.TicketResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TicketService {

    private static final Set<TicketStatus> ACTIVE_STATUSES = EnumSet.of(TicketStatus.OPEN, TicketStatus.IN_PROGRESS);

    private final TicketRepository ticketRepository;
    private final CommentRepository commentRepository;
    private final StatusHistoryRepository statusHistoryRepository;

    public TicketService(
            TicketRepository ticketRepository,
            CommentRepository commentRepository,
            StatusHistoryRepository statusHistoryRepository) {
        this.ticketRepository = ticketRepository;
        this.commentRepository = commentRepository;
        this.statusHistoryRepository = statusHistoryRepository;
    }

    @Transactional
    public TicketResponse create(CreateTicketRequest request, AuthenticatedUser user) {
        Ticket ticket = new Ticket();
        ticket.setTitle(request.title());
        ticket.setDescription(request.description());
        ticket.setPriority(request.priority());
        ticket.setStatus(TicketStatus.OPEN);
        ticket.setRequesterId(user.id());
        ticket.setSlaDueAt(Instant.now().plus(request.priority().slaWindow()));
        ticket = ticketRepository.save(ticket);
        recordTransition(ticket, null, TicketStatus.OPEN, user.id());
        return TicketResponse.from(ticket);
    }

    @Transactional(readOnly = true)
    public TicketResponse get(Long id, AuthenticatedUser user) {
        return TicketResponse.from(loadAccessible(id, user));
    }

    @Transactional(readOnly = true)
    public Page<TicketResponse> search(TicketStatus status, TicketPriority priority, Long assigneeId,
                                       boolean unassigned, Pageable pageable, AuthenticatedUser user) {
        Specification<Ticket> spec = Specification.allOf(
                TicketSpecifications.hasStatus(status),
                TicketSpecifications.hasPriority(priority),
                TicketSpecifications.hasAssignee(assigneeId),
                TicketSpecifications.isUnassigned(unassigned));
        if (user.isRequester()) {
            spec = spec.and(TicketSpecifications.hasRequester(user.id()));
        }
        return ticketRepository.findAll(spec, pageable).map(TicketResponse::from);
    }

    @Transactional
    public TicketResponse updateStatus(Long id, TicketStatus target, AuthenticatedUser user) {
        Ticket ticket = ticketRepository.findById(id).orElseThrow(() -> new TicketNotFoundException(id));
        TicketStatus current = ticket.getStatus();
        if (!current.canTransitionTo(target)) {
            throw new InvalidStatusTransitionException(current, target);
        }
        ticket.setStatus(target);
        ticket = ticketRepository.save(ticket);
        recordTransition(ticket, current, target, user.id());
        return TicketResponse.from(ticket);
    }

    @Transactional
    public TicketResponse updateAssignee(Long id, Long assigneeId) {
        Ticket ticket = ticketRepository.findById(id).orElseThrow(() -> new TicketNotFoundException(id));
        ticket.setAssigneeId(assigneeId);
        return TicketResponse.from(ticketRepository.save(ticket));
    }

    @Transactional
    public CommentResponse addComment(Long ticketId, CommentRequest request, AuthenticatedUser user) {
        Ticket ticket = loadAccessible(ticketId, user);
        Comment comment = new Comment();
        comment.setTicket(ticket);
        comment.setAuthorId(user.id());
        comment.setBody(request.body());
        return CommentResponse.from(commentRepository.save(comment));
    }

    @Transactional(readOnly = true)
    public List<CommentResponse> comments(Long ticketId, AuthenticatedUser user) {
        Ticket ticket = loadAccessible(ticketId, user);
        return commentRepository.findByTicketIdOrderByCreatedAtAsc(ticket.getId()).stream()
                .map(CommentResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<StatusHistoryResponse> history(Long ticketId, AuthenticatedUser user) {
        Ticket ticket = loadAccessible(ticketId, user);
        return statusHistoryRepository.findByTicketIdOrderByChangedAtAsc(ticket.getId()).stream()
                .map(StatusHistoryResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<TicketResponse> findSlaBreaches() {
        return ticketRepository.findSlaBreached(Instant.now(), ACTIVE_STATUSES).stream()
                .map(TicketResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<AgingReportRow> agingReport() {
        Instant now = Instant.now();
        return ticketRepository.aggregateAging().stream()
                .map(row -> new AgingReportRow(
                        row.getStatus(),
                        row.getTicketCount(),
                        Duration.between(row.getOldestCreatedAt(), now).toHours()))
                .toList();
    }

    private Ticket loadAccessible(Long id, AuthenticatedUser user) {
        Ticket ticket = ticketRepository.findById(id).orElseThrow(() -> new TicketNotFoundException(id));
        if (user.isRequester() && !ticket.getRequesterId().equals(user.id())) {
            throw new AccessDeniedException("You do not have access to ticket " + id);
        }
        return ticket;
    }

    private void recordTransition(Ticket ticket, TicketStatus from, TicketStatus to, Long changedBy) {
        StatusHistory entry = new StatusHistory();
        entry.setTicket(ticket);
        entry.setFromStatus(from);
        entry.setToStatus(to);
        entry.setChangedBy(changedBy);
        statusHistoryRepository.save(entry);
    }
}
