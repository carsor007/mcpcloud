"""Audit log — records every MCP tool call: who called what, when, and how it went.

Every call is also emitted as a structured JSON log line via structlog, so it
flows into CloudWatch/any log pipeline for SIEM ingestion. This module additionally
keeps a queryable ring buffer (Redis-backed, capped) for the /api/audit endpoint
and the Audit Log UI page.
"""

import json
import time
from typing import Any, Optional

import structlog

logger = structlog.get_logger()

_KEY = "mcpcloud:audit:log"
_MAX = 1000
_ARG_LIMIT = 2000

_local: list[dict] = []


async def _r():
    from session import get_tracker
    return await get_tracker()._r()


def _truncate(value: Any) -> Any:
    serialized = json.dumps(value, default=str)
    if len(serialized) <= _ARG_LIMIT:
        return value
    return {"_truncated": True, "preview": serialized[:_ARG_LIMIT]}


async def record(
    *,
    agent_type: str,
    skill_name: str,
    company_id: str,
    trace_id: Optional[str],
    mcp_session_id: Optional[str],
    arguments: dict[str, Any],
    success: bool,
    error: Optional[str],
    duration_ms: float,
) -> None:
    entry = {
        "ts": time.time(),
        "tool": f"{agent_type}__{skill_name}",
        "agent_type": agent_type,
        "skill_name": skill_name,
        "company_id": company_id,
        "trace_id": trace_id,
        "mcp_session_id": mcp_session_id,
        "arguments": _truncate(arguments),
        "success": success,
        "error": error[:500] if error else None,
        "duration_ms": round(duration_ms, 2),
    }

    logger.info("audit", **entry)

    r = await _r()
    if r:
        await r.lpush(_KEY, json.dumps(entry))
        await r.ltrim(_KEY, 0, _MAX - 1)
    else:
        _local.insert(0, entry)
        del _local[_MAX:]


async def list_entries(
    agent_type: Optional[str] = None,
    skill_name: Optional[str] = None,
    limit: int = 100,
) -> list[dict]:
    r = await _r()
    if r:
        entries = [json.loads(x) for x in await r.lrange(_KEY, 0, _MAX - 1)]
    else:
        entries = list(_local)

    if agent_type:
        entries = [e for e in entries if e["agent_type"] == agent_type]
    if skill_name:
        entries = [e for e in entries if e["skill_name"] == skill_name]

    return entries[:limit]
