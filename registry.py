"""Skill registry — maps (agent_type, skill_name) to async callables."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger()

SkillFn = Callable[[Dict[str, Any], Dict[str, Any]], Any]  # (input, context) → SkillResult

_DEFAULT_SCHEMA: Dict[str, Any] = {"type": "object", "additionalProperties": True}


@dataclass
class SkillResult:
    """Standardised return value from every skill function."""

    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """Holds all registered skills, keyed by agent_type → skill_name."""

    def __init__(self) -> None:
        self._skills: Dict[str, Dict[str, SkillFn]] = {}
        self._schemas: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def register(
        self,
        agent_type: str,
        skill_name: str,
        fn: SkillFn,
        schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._skills.setdefault(agent_type, {})[skill_name] = fn
        self._schemas.setdefault(agent_type, {})[skill_name] = schema or _DEFAULT_SCHEMA
        logger.debug("Skill registered", agent_type=agent_type, skill=skill_name)

    def get(self, agent_type: str, skill_name: str) -> Optional[SkillFn]:
        return self._skills.get(agent_type, {}).get(skill_name)

    def get_schema(self, agent_type: str, skill_name: str) -> Dict[str, Any]:
        return self._schemas.get(agent_type, {}).get(skill_name, _DEFAULT_SCHEMA)

    def list_skills(self, agent_type: str) -> List[str]:
        return list(self._skills.get(agent_type, {}).keys())

    def list_agent_types(self) -> List[str]:
        return list(self._skills.keys())

    def list_skills_with_meta(
        self, agent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        result = []
        types = [agent_type] if agent_type else self.list_agent_types()
        for at in types:
            for skill_name in self.list_skills(at):
                fn = self._skills[at][skill_name]
                result.append({
                    "agent_type": at,
                    "skill_name": skill_name,
                    "description": (fn.__doc__ or "").strip().splitlines()[0],
                    "schema": self.get_schema(at, skill_name),
                })
        return result


_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    return _registry
