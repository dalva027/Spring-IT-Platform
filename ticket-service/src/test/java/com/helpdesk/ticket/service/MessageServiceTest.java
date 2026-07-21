package com.helpdesk.ticket.service;

import java.util.Optional;

import com.helpdesk.ticket.domain.Message;
import com.helpdesk.ticket.exception.MessageNotFoundException;
import com.helpdesk.ticket.repository.MessageRepository;
import com.helpdesk.ticket.security.AuthenticatedUser;
import com.helpdesk.ticket.web.dto.MessageResponse;
import com.helpdesk.ticket.web.dto.SendMessageRequest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.access.AccessDeniedException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class MessageServiceTest {

    @Mock
    private MessageRepository messageRepository;

    @InjectMocks
    private MessageService messageService;

    private final AuthenticatedUser alice = new AuthenticatedUser(1L, "alice@example.com", "AGENT");
    private final AuthenticatedUser bob = new AuthenticatedUser(2L, "bob@example.com", "REQUESTER");
    private final AuthenticatedUser carol = new AuthenticatedUser(3L, "carol@example.com", "AGENT");

    @Test
    void sendRejectsMessagingYourself() {
        SendMessageRequest request = new SendMessageRequest(1L, "Hi", "note to self", null, null);

        assertThatThrownBy(() -> messageService.send(request, alice))
                .isInstanceOf(IllegalArgumentException.class);

        verify(messageRepository, never()).save(any());
    }

    @Test
    void replyInheritsThreadRootFromParent() {
        Message parent = message(10L, alice.id(), bob.id());
        parent.setRootId(null); // parent is itself the thread root
        when(messageRepository.findById(10L)).thenReturn(Optional.of(parent));
        when(messageRepository.save(any(Message.class))).thenAnswer(inv -> inv.getArgument(0));

        messageService.send(new SendMessageRequest(alice.id(), "Re: Hi", "reply", null, 10L), bob);

        ArgumentCaptor<Message> captor = ArgumentCaptor.forClass(Message.class);
        verify(messageRepository).save(captor.capture());
        assertThat(captor.getValue().getParentId()).isEqualTo(10L);
        assertThat(captor.getValue().getRootId()).isEqualTo(10L);
    }

    @Test
    void readingReceivedMessageMarksItRead() {
        Message message = message(5L, alice.id(), bob.id());
        when(messageRepository.findById(5L)).thenReturn(Optional.of(message));
        when(messageRepository.save(any(Message.class))).thenAnswer(inv -> inv.getArgument(0));

        MessageResponse response = messageService.get(5L, bob);

        assertThat(response.read()).isTrue();
        assertThat(response.readAt()).isNotNull();
        verify(messageRepository).save(message);
    }

    @Test
    void readingSentMessageDoesNotMarkRead() {
        Message message = message(5L, alice.id(), bob.id());
        when(messageRepository.findById(5L)).thenReturn(Optional.of(message));

        MessageResponse response = messageService.get(5L, alice);

        assertThat(response.read()).isFalse();
        verify(messageRepository, never()).save(any());
    }

    @Test
    void nonParticipantCannotReadMessage() {
        Message message = message(5L, alice.id(), bob.id());
        when(messageRepository.findById(5L)).thenReturn(Optional.of(message));

        assertThatThrownBy(() -> messageService.get(5L, carol))
                .isInstanceOf(AccessDeniedException.class);
    }

    @Test
    void unknownMessageThrowsNotFound() {
        when(messageRepository.findById(5L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> messageService.get(5L, alice))
                .isInstanceOf(MessageNotFoundException.class);
    }

    private Message message(Long id, Long senderId, Long recipientId) {
        Message message = new Message();
        setId(message, id);
        message.setSenderId(senderId);
        message.setRecipientId(recipientId);
        message.setSubject("Hi");
        message.setBody("hello");
        return message;
    }

    // id has no setter (DB-generated); set it reflectively for the test fixtures.
    private void setId(Message message, Long id) {
        try {
            var field = Message.class.getDeclaredField("id");
            field.setAccessible(true);
            field.set(message, id);
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException(e);
        }
    }
}
