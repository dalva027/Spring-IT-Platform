package com.helpdesk.ticket.service;

import java.time.Instant;
import java.util.List;

import com.helpdesk.ticket.domain.Message;
import com.helpdesk.ticket.exception.MessageNotFoundException;
import com.helpdesk.ticket.repository.MessageRepository;
import com.helpdesk.ticket.security.AuthenticatedUser;
import com.helpdesk.ticket.web.dto.MessageResponse;
import com.helpdesk.ticket.web.dto.SendMessageRequest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class MessageService {

    private final MessageRepository messageRepository;

    public MessageService(MessageRepository messageRepository) {
        this.messageRepository = messageRepository;
    }

    @Transactional
    public MessageResponse send(SendMessageRequest request, AuthenticatedUser user) {
        if (request.recipientId().equals(user.id())) {
            throw new IllegalArgumentException("You cannot send a message to yourself.");
        }

        Message message = new Message();
        message.setSenderId(user.id());
        message.setRecipientId(request.recipientId());
        message.setSubject(request.subject());
        message.setBody(request.body());
        message.setTicketId(request.ticketId());

        if (request.parentId() != null) {
            Message parent = loadParticipating(request.parentId(), user);
            message.setParentId(parent.getId());
            message.setRootId(effectiveRoot(parent));
        }

        return MessageResponse.from(messageRepository.save(message));
    }

    @Transactional(readOnly = true)
    public Page<MessageResponse> inbox(AuthenticatedUser user, Pageable pageable) {
        return messageRepository.findByRecipientIdOrderByCreatedAtDesc(user.id(), pageable)
                .map(MessageResponse::from);
    }

    @Transactional(readOnly = true)
    public Page<MessageResponse> sent(AuthenticatedUser user, Pageable pageable) {
        return messageRepository.findBySenderIdOrderByCreatedAtDesc(user.id(), pageable)
                .map(MessageResponse::from);
    }

    /** Reading a message you received marks it read as a side effect. */
    @Transactional
    public MessageResponse get(Long id, AuthenticatedUser user) {
        Message message = loadParticipating(id, user);
        markReadIfRecipient(message, user);
        return MessageResponse.from(message);
    }

    /** The whole conversation the message belongs to (only the parts this user is party to). */
    @Transactional
    public List<MessageResponse> thread(Long id, AuthenticatedUser user) {
        Message message = loadParticipating(id, user);
        markReadIfRecipient(message, user);
        return messageRepository.findThread(effectiveRoot(message), user.id()).stream()
                .map(MessageResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public long unreadCount(AuthenticatedUser user) {
        return messageRepository.countByRecipientIdAndReadFalse(user.id());
    }

    @Transactional
    public MessageResponse markRead(Long id, AuthenticatedUser user) {
        Message message = loadParticipating(id, user);
        if (!user.id().equals(message.getRecipientId())) {
            throw new AccessDeniedException("Only the recipient can mark a message read.");
        }
        markReadIfRecipient(message, user);
        return MessageResponse.from(message);
    }

    private Message loadParticipating(Long id, AuthenticatedUser user) {
        Message message = messageRepository.findById(id).orElseThrow(() -> new MessageNotFoundException(id));
        boolean participant = user.id().equals(message.getSenderId())
                || user.id().equals(message.getRecipientId());
        if (!participant) {
            throw new AccessDeniedException("You do not have access to message " + id);
        }
        return message;
    }

    private void markReadIfRecipient(Message message, AuthenticatedUser user) {
        if (!message.isRead() && user.id().equals(message.getRecipientId())) {
            message.setRead(true);
            message.setReadAt(Instant.now());
            messageRepository.save(message);
        }
    }

    /** A reply's thread root, or the message's own id when it is itself the root. */
    private Long effectiveRoot(Message message) {
        return message.getRootId() != null ? message.getRootId() : message.getId();
    }
}
