"""Dynamic skill storage — Redis-backed with in-memory fallback.

Keys:
  mcpcloud:dynsk:index              → Redis set of "agent_type:skill_name"
  mcpcloud:dynsk:{at}:{sn}:code    → Python source string
  mcpcloud:dynsk:logs:{at}:{sn}    → Redis list of JSON log entries (capped at 20)
"""

import json
import time
from typing import Optional

PREFIX = "mcpcloud:dynsk"

_local: dict[str, str] = {}
_logs: dict[str, list] = {}


async def _r():
    from session import get_tracker
    return await get_tracker()._r()


async def save_skill(agent_type: str, skill_name: str, code: str) -> None:
    r = await _r()
    if r:
        await r.set(f"{PREFIX}:{agent_type}:{skill_name}:code", code)
        await r.sadd(f"{PREFIX}:index", f"{agent_type}:{skill_name}")
    else:
        _local[f"{agent_type}:{skill_name}"] = code


async def get_skill(agent_type: str, skill_name: str) -> Optional[str]:
    r = await _r()
    if r:
        return await r.get(f"{PREFIX}:{agent_type}:{skill_name}:code")
    return _local.get(f"{agent_type}:{skill_name}")


async def delete_skill(agent_type: str, skill_name: str) -> bool:
    r = await _r()
    if r:
        deleted = await r.delete(f"{PREFIX}:{agent_type}:{skill_name}:code")
        await r.srem(f"{PREFIX}:index", f"{agent_type}:{skill_name}")
        return deleted > 0
    key = f"{agent_type}:{skill_name}"
    if key in _local:
        del _local[key]
        return True
    return False


async def append_log(agent_type: str, skill_name: str, success: bool, error: str | None) -> None:
    entry = json.dumps({"ts": time.time(), "success": success, "error": error})
    r = await _r()
    key = f"{PREFIX}:logs:{agent_type}:{skill_name}"
    if r:
        await r.lpush(key, entry)
        await r.ltrim(key, 0, 19)
    else:
        _logs.setdefault(key, []).insert(0, json.loads(entry))
        _logs[key] = _logs[key][:20]


async def get_logs(agent_type: str, skill_name: str) -> list:
    r = await _r()
    key = f"{PREFIX}:logs:{agent_type}:{skill_name}"
    if r:
        return [json.loads(x) for x in await r.lrange(key, 0, 19)]
    return _logs.get(key, [])


async def list_skills() -> list[dict]:
    r = await _r()
    if r:
        members = await r.smembers(f"{PREFIX}:index")
        result = []
        for m in sorted(members):
            at, sn = m.split(":", 1)
            result.append({"agent_type": at, "skill_name": sn})
        return result
    return [
        {"agent_type": k.split(":", 1)[0], "skill_name": k.split(":", 1)[1]}
        for k in sorted(_local)
    ]
