"""Jira Operations — create, retrieve, and search Jira issues.

To connect to a real Jira instance, set in .env:
    JIRA_URL        = https://your-domain.atlassian.net
    JIRA_EMAIL      = you@company.com
    JIRA_API_TOKEN  = your-api-token   # atlassian.com/manage-profile/security/api-tokens
    JIRA_PROJECT    = IT               # default project key

Without these, skills return realistic stub data so you can develop
and test your workflows before wiring up credentials.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict

import httpx

from registry import SkillResult, get_registry

_URL   = os.getenv("JIRA_URL", "")
_EMAIL = os.getenv("JIRA_EMAIL", "")
_TOKEN = os.getenv("JIRA_API_TOKEN", "")
_PROJ  = os.getenv("JIRA_PROJECT", "IT")

_CONFIGURED = bool(_URL and _EMAIL and _TOKEN)

_PRIORITY_MAP = {
    "critical": "Highest",
    "high":     "High",
    "normal":   "Medium",
    "low":      "Low",
}


async def create_ticket(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Create a Jira issue and return its key and URL.

    Input: { "summary": "...", "description": "...",
             "priority": "high|normal|low|critical",
             "type": "Bug|Task|Story" }
    """
    summary     = input.get("summary", "").strip()
    description = input.get("description", "")
    priority    = _PRIORITY_MAP.get(input.get("priority", "normal"), "Medium")
    issue_type  = input.get("type", "Task")
    project     = input.get("project", _PROJ)

    if not summary:
        return SkillResult(success=False, output={}, error="'summary' is required")

    if _CONFIGURED:
        # ── Real Jira call ────────────────────────────────────────────────────
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_URL}/rest/api/2/issue",
                auth=(_EMAIL, _TOKEN),
                json={
                    "fields": {
                        "project":     {"key": project},
                        "summary":     summary,
                        "description": description,
                        "issuetype":   {"name": issue_type},
                        "priority":    {"name": priority},
                    }
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            key  = data["key"]
            return SkillResult(success=True, output={
                "key": key,
                "url": f"{_URL}/browse/{key}",
                "summary":  summary,
                "priority": priority,
                "status":   "Open",
            })
        # ─────────────────────────────────────────────────────────────────────

    # Stub — remove once JIRA_URL / JIRA_EMAIL / JIRA_API_TOKEN are set
    key = f"{project}-{int(uuid.uuid4().int % 9000) + 1000}"
    return SkillResult(success=True, output={
        "key":     key,
        "url":     f"https://your-domain.atlassian.net/browse/{key}",
        "summary": summary,
        "priority": priority,
        "status":  "Open",
        "_stub":   True,
    })


async def get_ticket(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Fetch the status, assignee, and priority of a Jira issue by key.

    Input: { "key": "IT-1234" }
    """
    key = input.get("key", "").strip().upper()
    if not key:
        return SkillResult(success=False, output={}, error="'key' is required")

    if _CONFIGURED:
        # ── Real Jira call ────────────────────────────────────────────────────
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_URL}/rest/api/2/issue/{key}",
                auth=(_EMAIL, _TOKEN),
                params={"fields": "summary,status,assignee,priority,created,updated"},
                timeout=10,
            )
            resp.raise_for_status()
            f = resp.json()["fields"]
            return SkillResult(success=True, output={
                "key":      key,
                "url":      f"{_URL}/browse/{key}",
                "summary":  f.get("summary"),
                "status":   f["status"]["name"],
                "priority": f["priority"]["name"],
                "assignee": f["assignee"]["displayName"] if f.get("assignee") else "Unassigned",
                "created":  f.get("created"),
                "updated":  f.get("updated"),
            })
        # ─────────────────────────────────────────────────────────────────────

    # Stub
    return SkillResult(success=True, output={
        "key":      key,
        "url":      f"https://your-domain.atlassian.net/browse/{key}",
        "summary":  f"Issue {key}",
        "status":   "In Progress",
        "priority": "Medium",
        "assignee": "Jane Smith",
        "created":  "2026-06-20T09:00:00.000+0000",
        "updated":  "2026-06-24T14:32:00.000+0000",
        "_stub":    True,
    })


async def search_tickets(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Search Jira issues using JQL and return a summary list.

    Input: { "jql": "project = IT AND status != Done AND priority = High",
             "limit": 10 }
    """
    jql   = input.get("jql", f"project = {_PROJ} AND status != Done ORDER BY priority DESC")
    limit = min(int(input.get("limit", 10)), 50)

    if _CONFIGURED:
        # ── Real Jira call ────────────────────────────────────────────────────
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_URL}/rest/api/2/search",
                auth=(_EMAIL, _TOKEN),
                params={
                    "jql":        jql,
                    "maxResults": limit,
                    "fields":     "summary,status,assignee,priority",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            issues = [
                {
                    "key":      i["key"],
                    "url":      f"{_URL}/browse/{i['key']}",
                    "summary":  i["fields"]["summary"],
                    "status":   i["fields"]["status"]["name"],
                    "priority": i["fields"]["priority"]["name"],
                    "assignee": i["fields"]["assignee"]["displayName"]
                               if i["fields"].get("assignee") else "Unassigned",
                }
                for i in data.get("issues", [])
            ]
            return SkillResult(success=True, output={
                "total":  data.get("total", len(issues)),
                "issues": issues,
                "jql":    jql,
            })
        # ─────────────────────────────────────────────────────────────────────

    # Stub
    return SkillResult(success=True, output={
        "total": 3,
        "issues": [
            {"key": f"{_PROJ}-1021", "url": f"https://your-domain.atlassian.net/browse/{_PROJ}-1021",
             "summary": "VPN login failing after Windows update", "status": "Open",     "priority": "High",   "assignee": "Network Ops"},
            {"key": f"{_PROJ}-1019", "url": f"https://your-domain.atlassian.net/browse/{_PROJ}-1019",
             "summary": "Outlook calendar not syncing on mobile",  "status": "In Progress", "priority": "Medium", "assignee": "Jane Smith"},
            {"key": f"{_PROJ}-1015", "url": f"https://your-domain.atlassian.net/browse/{_PROJ}-1015",
             "summary": "Printer offline — 3rd floor",             "status": "Open",     "priority": "Low",    "assignee": "Unassigned"},
        ],
        "jql":   jql,
        "_stub": True,
    })


def register_all() -> None:
    registry = get_registry()

    registry.register(
        "jira_ops", "create_ticket", create_ticket,
        schema={
            "type": "object",
            "required": ["summary"],
            "properties": {
                "summary":     {"type": "string",  "description": "Issue title."},
                "description": {"type": "string",  "description": "Full description."},
                "priority":    {"type": "string",  "enum": ["critical", "high", "normal", "low"]},
                "type":        {"type": "string",  "enum": ["Task", "Bug", "Story"], "description": "Issue type (default Task)."},
                "project":     {"type": "string",  "description": f"Project key (default {_PROJ})."},
            },
        },
    )

    registry.register(
        "jira_ops", "get_ticket", get_ticket,
        schema={
            "type": "object",
            "required": ["key"],
            "properties": {
                "key": {"type": "string", "description": "Jira issue key, e.g. IT-1234."},
            },
        },
    )

    registry.register(
        "jira_ops", "search_tickets", search_tickets,
        schema={
            "type": "object",
            "properties": {
                "jql":   {"type": "string",  "description": "JQL query string."},
                "limit": {"type": "integer", "description": "Max results (default 10)."},
            },
        },
    )
