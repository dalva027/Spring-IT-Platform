package com.helpdesk.ticket.repository;

import java.util.List;

import com.helpdesk.ticket.domain.Comment;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CommentRepository extends JpaRepository<Comment, Long> {

    List<Comment> findByTicketIdOrderByCreatedAtAsc(Long ticketId);
}
