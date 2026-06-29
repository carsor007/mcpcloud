"""Dynamic skill loader — exec()s Python code stored in Redis and registers
the functions in the skill registry at runtime.

Skill code must define an async function whose name matches skill_name:
    async def my_skill(input: dict, ctx: dict) -> dict:
        return {"success": True, "result": ...}

Optionally define a module-level SCHEMA dict for JSON Schema validation.
"""

import structlog

from registry import SkillResult, get_registry
from skills_store import get_skill, list_skills

logger = structlog.get_logger()


async def load_all() -> None:
    skills = await list_skills()
    loaded, failed = [], []
    for s in skills:
        ok = await load_one(s["agent_type"], s["skill_name"])
        (loaded if ok else failed).append(f"{s['agent_type']}:{s['skill_name']}")
    logger.info("Dynamic skills loaded", loaded=loaded, failed=failed)


async def load_one(agent_type: str, skill_name: str) -> bool:
    code = await get_skill(agent_type, skill_name)
    if not code:
        return False
    try:
        ns: dict = {}
        exec(compile(code, f"<skill:{agent_type}:{skill_name}>", "exec"), ns)
        fn = ns.get(skill_name)
        if not callable(fn):
            logger.warning(
                "Dynamic skill has no callable matching skill_name",
                agent_type=agent_type,
                skill_name=skill_name,
            )
            return False

        schema = ns.get("SCHEMA", {"type": "object", "properties": {}})

        async def _wrapped(input, ctx, _fn=fn):
            result = await _fn(input, ctx)
            if isinstance(result, SkillResult):
                return result
            if isinstance(result, dict):
                return SkillResult(
                    success=result.get("success", True),
                    output=result,
                    error=result.get("error"),
                )
            return SkillResult(success=True, output={"result": result})

        _wrapped.__doc__ = fn.__doc__

        get_registry().register(agent_type, skill_name, _wrapped, schema=schema)
        logger.info("Dynamic skill loaded", agent_type=agent_type, skill_name=skill_name)
        return True

    except Exception as e:
        logger.error(
            "Dynamic skill load failed",
            agent_type=agent_type,
            skill_name=skill_name,
            error=str(e),
        )
        return False
