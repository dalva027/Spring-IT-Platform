package com.helpdesk.ticket.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * @param ticketId optional ticket this message is about
 * @param parentId optional message being replied to (threads the conversation)
 */
public record SendMessageRequest(
        @NotNull Long recipientId,
        @NotBlank @Size(max = 200) String subject,
        @NotBlank @Size(max = 5000) String body,
        Long ticketId,
        Long parentId) {
}
