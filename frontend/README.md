# Helpdesk Frontend

React + TypeScript SPA for the IT ticketing platform, built with Vite. Visual language
follows the design system in `devtools/DESIGN.md` (Inter, black pill buttons, mint-green
accent, flat hairline-bordered cards).

## Run

Requires auth-service (:8081) and ticket-service (:8082) to be up — e.g.
`docker compose up --build` from the repo root.

```bash
npm install
npm run dev      # http://localhost:5173 (already CORS-whitelisted by both services)
npm run build    # type-check + production bundle in dist/
npm run lint
```

To point at other backends set `VITE_AUTH_API_URL` / `VITE_TICKET_API_URL` (e.g. in `.env.local`).

## Structure

```
src/
├── api/          # fetch wrapper (JWT, error handling), typed endpoints, DTO types
├── auth/         # AuthContext (session), UserDirectoryContext (id → name lookup)
├── components/   # Layout/topbar, badges, SLA indicator, pagination, feedback
└── pages/        # Login, Register, Tickets, NewTicket, TicketDetail, Reports, Users
```

## Features

- JWT auth with persisted session; login/register; automatic logout on 401
- Ticket queue with status/priority filters, "assigned to me", URL-backed state, paging
- Ticket detail: comments, status audit trail, live SLA countdown (green/amber/red),
  and — for agents/admins — only the status transitions the backend state machine allows,
  plus an assignee picker
- Reports (agents/admins): ticket aging and SLA breaches
- Users (agents/admins): directory with role badges; admins can change roles
- Requesters see their own tickets only, mirroring the backend rules
- Dark mode: toggle in the topbar (and on the auth pages), persisted in localStorage,
  defaults to the OS preference and applied before first paint to avoid a flash
