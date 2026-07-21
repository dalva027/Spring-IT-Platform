package com.helpdesk.ticket.repository;

import java.util.List;

import com.helpdesk.ticket.domain.Message;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface MessageRepository extends JpaRepository<Message, Long> {

    Page<Message> findByRecipientIdOrderByCreatedAtDesc(Long recipientId, Pageable pageable);

    Page<Message> findBySenderIdOrderByCreatedAtDesc(Long senderId, Pageable pageable);

    long countByRecipientIdAndReadFalse(Long recipientId);

    /**
     * Every message in a thread that the given user is party to, oldest first.
     * A thread is identified by its root id: the root itself ({@code id = :root})
     * plus every reply that points at it ({@code rootId = :root}).
     */
    @Query("""
            select m from Message m
            where (m.rootId = :root or m.id = :root)
              and (m.senderId = :userId or m.recipientId = :userId)
            order by m.createdAt asc
            """)
    List<Message> findThread(@Param("root") Long root, @Param("userId") Long userId);
}
