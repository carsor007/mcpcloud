"""Audit log API — query recorded MCP tool-call history."""

from typing import Optional

from fastapi import APIRouter

from audit import list_entries

router = APIRouter()


@router.get("")
async def get_audit_log(
    agent_type: Optional[str] = None,
    skill_name: Optional[str] = None,
    limit: int = 100,
):
    limit = max(1, min(limit, 1000))
    entries = await list_entries(agent_type=agent_type, skill_name=skill_name, limit=limit)
    return {"entries": entries}
