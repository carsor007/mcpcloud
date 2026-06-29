"""Skills CRUD API — create, read, update, delete dynamic skills."""

import re

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from registry import get_registry
from skills.dynamic import load_one
from skills_store import delete_skill, get_logs, get_skill, list_skills, save_skill

logger = structlog.get_logger()
router = APIRouter()

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")

_TEMPLATE = '''\
import httpx
import os

async def {skill_name}(input: dict, ctx: dict) -> dict:
    """Describe what this skill does."""
    # Read credentials from environment variables:
    # api_key = os.environ.get("MY_API_KEY", "")

    param = input.get("param", "")

    # async with httpx.AsyncClient() as client:
    #     resp = await client.get("https://api.example.com", ...)

    return {{"success": True, "result": param}}


# Optional: JSON Schema for inputs shown in the tool browser
# SCHEMA = {{
#     "type": "object",
#     "properties": {{
#         "param": {{"type": "string", "description": "..."}}
#     }}
# }}
'''


def _validate_name(value: str, field: str) -> str:
    v = value.strip().lower().replace("-", "_")
    if not _NAME_RE.match(v):
        raise HTTPException(
            400, f"{field} must start with a letter and contain only a-z, 0-9, _"
        )
    return v


class SkillSave(BaseModel):
    agent_type: str
    skill_name: str
    code: str


@router.get("")
async def list_all():
    skills = await list_skills()
    registry = get_registry()
    for s in skills:
        s["loaded"] = registry.get(s["agent_type"], s["skill_name"]) is not None
    return {"skills": skills}


@router.get("/template")
async def get_template(skill_name: str = "my_skill"):
    safe = _NAME_RE.sub("", skill_name.lower().replace("-", "_")) or "my_skill"
    return {"code": _TEMPLATE.format(skill_name=safe)}


@router.get("/{agent_type}/{skill_name}/logs")
async def get_skill_logs(agent_type: str, skill_name: str):
    return {"logs": await get_logs(agent_type, skill_name)}


@router.get("/{agent_type}/{skill_name}")
async def get_skill_code(agent_type: str, skill_name: str):
    code = await get_skill(agent_type, skill_name)
    if code is None:
        raise HTTPException(404, "Skill not found")
    return {"agent_type": agent_type, "skill_name": skill_name, "code": code}


@router.post("")
async def save_skill_endpoint(body: SkillSave):
    at = _validate_name(body.agent_type, "agent_type")
    sn = _validate_name(body.skill_name, "skill_name")

    if not body.code.strip():
        raise HTTPException(400, "code is required")

    await save_skill(at, sn, body.code)
    ok = await load_one(at, sn)
    if not ok:
        raise HTTPException(422, "Saved but failed to load — check your syntax and function name")

    logger.info("Dynamic skill saved and loaded", agent_type=at, skill_name=sn)
    return {"ok": True, "agent_type": at, "skill_name": sn}


@router.delete("/{agent_type}/{skill_name}")
async def delete_skill_endpoint(agent_type: str, skill_name: str):
    deleted = await delete_skill(agent_type, skill_name)
    if not deleted:
        raise HTTPException(404, "Skill not found")

    registry = get_registry()
    if agent_type in getattr(registry, "_skills", {}):
        registry._skills[agent_type].pop(skill_name, None)

    logger.info("Dynamic skill deleted", agent_type=agent_type, skill_name=skill_name)
    return {"ok": True}
