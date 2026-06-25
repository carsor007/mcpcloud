"""
MCP session tracker.

Maps Mcp-Session-Id tokens to session metadata (trace_id, agent_type, etc.).

Two backends:
  - In-process dict  (default, single-worker / dev)
  - Redis            (set REDIS_URL; fixes session loss across workers)

Tool execution is stateless — only session logging is affected when a client's
initialize and tools/call requests hit different workers.
"""

import json
import uuid
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger()

_SESSION_TTL = 3600  # seconds


class SessionTracker:
    def __init__(self, redis_url: str = "") -> None:
        self._local: Dict[str, Dict[str, Any]] = {}
        self._redis_url = redis_url
        self._redis = None

    async def _r(self):
        if self._redis is None and self._redis_url:
            import redis.asyncio as aioredis
            self._redis = await aioredis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    async def create(
        self,
        agent_type: Optional[str],
        client_info: Dict[str, Any],
        protocol_version: Optional[str],
    ) -> tuple[str, str]:
        """Create a new MCP session. Returns (mcp_session_id, trace_id)."""
        mcp_sid = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        entry: Dict[str, Any] = {
            "mcp_sid": mcp_sid,
            "trace_id": trace_id,
            "agent_type": agent_type or "all",
            "client_info": client_info,
            "protocol_version": protocol_version,
        }

        r = await self._r()
        if r:
            await r.setex(f"mcp:{mcp_sid}", _SESSION_TTL, json.dumps(entry))
        else:
            self._local[mcp_sid] = entry

        logger.info("MCP session created", mcp_session=mcp_sid, trace_id=trace_id)
        return mcp_sid, trace_id

    async def get(self, mcp_sid: str) -> Optional[Dict[str, Any]]:
        r = await self._r()
        if r:
            raw = await r.get(f"mcp:{mcp_sid}")
            return json.loads(raw) if raw else None
        return self._local.get(mcp_sid)

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None


_tracker: Optional[SessionTracker] = None


def get_tracker() -> SessionTracker:
    global _tracker
    if _tracker is None:
        from config.settings import get_settings
        _tracker = SessionTracker(redis_url=get_settings().REDIS_URL)
    return _tracker
