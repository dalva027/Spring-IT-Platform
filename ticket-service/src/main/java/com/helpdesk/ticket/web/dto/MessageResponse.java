package com.helpdesk.ticket.web.dto;

import java.time.Instant;

import com.helpdesk.ticket.domain.Message;

public record MessageResponse(
        Long id,
        Long senderId,
        Long recipientId,
        String subject,
        String body,
        Long ticketId,
        Long parentId,
        Long rootId,
        boolean read,
        Instant createdAt,
        Instant readAt) {

    public static MessageResponse from(Message message) {
        return new MessageResponse(
                message.getId(),
                message.getSenderId(),
                message.getRecipientId(),
                message.getSubject(),
                message.getBody(),
                message.getTicketId(),
                message.getParentId(),
                message.getRootId(),
                message.isRead(),
                message.getCreatedAt(),
                message.getReadAt());
    }
}
