package com.helpdesk.ticket.repository;

import com.helpdesk.ticket.domain.Ticket;
import com.helpdesk.ticket.domain.TicketPriority;
import com.helpdesk.ticket.domain.TicketStatus;
import org.springframework.data.jpa.domain.Specification;

/**
 * Composable filters for ticket search. A null argument yields a no-op filter,
 * so callers can combine them without null checks.
 */
public final class TicketSpecifications {

    private TicketSpecifications() {
    }

    public static Specification<Ticket> hasStatus(TicketStatus status) {
        return (root, query, cb) -> status == null ? cb.conjunction() : cb.equal(root.get("status"), status);
    }

    public static Specification<Ticket> hasPriority(TicketPriority priority) {
        return (root, query, cb) -> priority == null ? cb.conjunction() : cb.equal(root.get("priority"), priority);
    }

    public static Specification<Ticket> hasAssignee(Long assigneeId) {
        return (root, query, cb) -> assigneeId == null ? cb.conjunction() : cb.equal(root.get("assigneeId"), assigneeId);
    }

    /** Matches tickets with no assignee — the triage "inbox" queue. A false flag is a no-op. */
    public static Specification<Ticket> isUnassigned(boolean unassigned) {
        return (root, query, cb) -> unassigned ? cb.isNull(root.get("assigneeId")) : cb.conjunction();
    }

    public static Specification<Ticket> hasRequester(Long requesterId) {
        return (root, query, cb) -> cb.equal(root.get("requesterId"), requesterId);
    }
}
