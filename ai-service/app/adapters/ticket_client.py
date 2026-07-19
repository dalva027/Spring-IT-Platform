"""httpx client for ticket-service. The caller decides which token to use per
call: the employee's pass-through JWT for ticket creation, the minted service
AGENT token for comments/assignment/reads."""

from typing import Any

import httpx

from app.config import get_settings


class TicketServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(f"ticket-service {status_code}: {message}")
        self.status_code = status_code


class TicketClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or get_settings().ticket_api_url).rstrip("/")

    async def _request(
        self, method: str, path: str, token: str, json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(
                method,
                f"{self.base_url}{path}",
                json=json,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
        if response.status_code >= 400:
            raise TicketServiceError(response.status_code, response.text[:500])
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def create_ticket(
        self, token: str, title: str, description: str, priority: str
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/api/tickets",
            token,
            json={"title": title[:200], "description": description[:10000], "priority": priority},
        )

    async def get_ticket(self, token: str, ticket_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/tickets/{ticket_id}", token)

    async def add_comment(self, token: str, ticket_id: int, body: str) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/tickets/{ticket_id}/comments", token, json={"body": body[:5000]}
        )

    async def update_assignee(self, token: str, ticket_id: int, assignee_id: int) -> dict[str, Any]:
        return await self._request(
            "PATCH", f"/api/tickets/{ticket_id}/assignee", token, json={"assigneeId": assignee_id}
        )

    async def search_tickets(
        self, token: str, status: str, page: int = 0, size: int = 50
    ) -> dict[str, Any]:
        return await self._request(
            "GET", "/api/tickets", token, params={"status": status, "page": page, "size": size}
        )
