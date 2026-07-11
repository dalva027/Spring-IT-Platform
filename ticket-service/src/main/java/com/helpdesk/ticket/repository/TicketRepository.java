package com.helpdesk.ticket.repository;

import java.time.Instant;
import java.util.Collection;
import java.util.List;

import com.helpdesk.ticket.domain.Ticket;
import com.helpdesk.ticket.domain.TicketStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface TicketRepository extends JpaRepository<Ticket, Long>, JpaSpecificationExecutor<Ticket> {

    /**
     * Tickets whose SLA deadline has passed while still in an active (not yet resolved/closed) state.
     */
    @Query("""
            select t from Ticket t
            where t.slaDueAt < :now and t.status in :activeStatuses
            order by t.slaDueAt asc
            """)
    List<Ticket> findSlaBreached(@Param("now") Instant now,
                                 @Param("activeStatuses") Collection<TicketStatus> activeStatuses);

    /**
     * Ticket count and oldest creation timestamp per status, for the aging report.
     */
    @Query("""
            select t.status as status, count(t) as ticketCount, min(t.createdAt) as oldestCreatedAt
            from Ticket t
            group by t.status
            """)
    List<TicketAgingView> aggregateAging();
}
