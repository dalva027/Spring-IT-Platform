package com.helpdesk.ticket.web.dto;

import java.time.Instant;

import com.helpdesk.ticket.domain.Comment;

public record CommentResponse(Long id, Long ticketId, Long authorId, String body, Instant createdAt) {

    public static CommentResponse from(Comment comment) {
        return new CommentResponse(
                comment.getId(),
                comment.getTicket().getId(),
                comment.getAuthorId(),
                comment.getBody(),
                comment.getCreatedAt());
    }
}
