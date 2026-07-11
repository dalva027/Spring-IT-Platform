package com.helpdesk.ticket.repository;

import java.util.List;

import com.helpdesk.ticket.domain.StatusHistory;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StatusHistoryRepository extends JpaRepository<StatusHistory, Long> {

    List<StatusHistory> findByTicketIdOrderByChangedAtAsc(Long ticketId);
}
