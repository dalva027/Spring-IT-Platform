package com.helpdesk.ticket.web;

import java.util.List;

import com.helpdesk.ticket.domain.TicketPriority;
import com.helpdesk.ticket.domain.TicketStatus;
import com.helpdesk.ticket.security.AuthenticatedUser;
import com.helpdesk.ticket.service.TicketService;
import com.helpdesk.ticket.web.dto.AgingReportRow;
import com.helpdesk.ticket.web.dto.AssigneeUpdateRequest;
import com.helpdesk.ticket.web.dto.CommentRequest;
import com.helpdesk.ticket.web.dto.CommentResponse;
import com.helpdesk.ticket.web.dto.CreateTicketRequest;
import com.helpdesk.ticket.web.dto.StatusHistoryResponse;
import com.helpdesk.ticket.web.dto.StatusUpdateRequest;
import com.helpdesk.ticket.web.dto.TicketResponse;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
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
@RequestMapping("/api/tickets")
public class TicketController {

    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TicketResponse create(@Valid @RequestBody CreateTicketRequest request,
                                 @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.create(request, user);
    }

    @GetMapping
    public Page<TicketResponse> search(
            @RequestParam(required = false) TicketStatus status,
            @RequestParam(required = false) TicketPriority priority,
            @RequestParam(required = false) Long assigneeId,
            @RequestParam(required = false, defaultValue = "false") boolean unassigned,
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable,
            @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.search(status, priority, assigneeId, unassigned, pageable, user);
    }

    @GetMapping("/{id}")
    public TicketResponse get(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.get(id, user);
    }

    @PatchMapping("/{id}/status")
    @PreAuthorize("hasAnyRole('AGENT', 'ADMIN')")
    public TicketResponse updateStatus(@PathVariable Long id,
                                       @Valid @RequestBody StatusUpdateRequest request,
                                       @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.updateStatus(id, request.status(), user);
    }

    @PatchMapping("/{id}/assignee")
    @PreAuthorize("hasAnyRole('AGENT', 'ADMIN')")
    public TicketResponse updateAssignee(@PathVariable Long id,
                                         @Valid @RequestBody AssigneeUpdateRequest request) {
        return ticketService.updateAssignee(id, request.assigneeId());
    }

    @PostMapping("/{id}/comments")
    @ResponseStatus(HttpStatus.CREATED)
    public CommentResponse addComment(@PathVariable Long id,
                                      @Valid @RequestBody CommentRequest request,
                                      @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.addComment(id, request, user);
    }

    @GetMapping("/{id}/comments")
    public List<CommentResponse> comments(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.comments(id, user);
    }

    @GetMapping("/{id}/history")
    public List<StatusHistoryResponse> history(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return ticketService.history(id, user);
    }

    @GetMapping("/reports/sla-breaches")
    @PreAuthorize("hasAnyRole('AGENT', 'ADMIN')")
    public List<TicketResponse> slaBreaches() {
        return ticketService.findSlaBreaches();
    }

    @GetMapping("/reports/aging")
    @PreAuthorize("hasAnyRole('AGENT', 'ADMIN')")
    public List<AgingReportRow> agingReport() {
        return ticketService.agingReport();
    }
}
