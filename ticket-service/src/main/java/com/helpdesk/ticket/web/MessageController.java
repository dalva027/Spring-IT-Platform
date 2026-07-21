package com.helpdesk.ticket.web;

import java.util.List;
import java.util.Map;

import com.helpdesk.ticket.security.AuthenticatedUser;
import com.helpdesk.ticket.service.MessageService;
import com.helpdesk.ticket.web.dto.MessageResponse;
import com.helpdesk.ticket.web.dto.SendMessageRequest;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/messages")
public class MessageController {

    private final MessageService messageService;

    public MessageController(MessageService messageService) {
        this.messageService = messageService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public MessageResponse send(@Valid @RequestBody SendMessageRequest request,
                                @AuthenticationPrincipal AuthenticatedUser user) {
        return messageService.send(request, user);
    }

    /** {@code box=inbox} (default) lists messages received; {@code box=sent} lists messages sent. */
    @GetMapping
    public Page<MessageResponse> list(
            @RequestParam(defaultValue = "inbox") String box,
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable,
            @AuthenticationPrincipal AuthenticatedUser user) {
        return "sent".equalsIgnoreCase(box)
                ? messageService.sent(user, pageable)
                : messageService.inbox(user, pageable);
    }

    @GetMapping("/unread-count")
    public Map<String, Long> unreadCount(@AuthenticationPrincipal AuthenticatedUser user) {
        return Map.of("count", messageService.unreadCount(user));
    }

    @GetMapping("/{id}")
    public MessageResponse get(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return messageService.get(id, user);
    }

    @GetMapping("/{id}/thread")
    public List<MessageResponse> thread(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return messageService.thread(id, user);
    }

    @PatchMapping("/{id}/read")
    public MessageResponse markRead(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return messageService.markRead(id, user);
    }
}
