"""
MCP (Model Context Protocol) HTTP endpoint — Streamable HTTP transport.

Spec: https://spec.modelcontextprotocol.io/specification/2025-03-26/

Every skill registered in the SkillRegistry is exposed as an MCP tool,
making any function consumable from Claude Desktop, Cursor, Zed, VS Code,
or any MCP-compatible client.

Routes
------
POST /mcp                      — all agent types as tools
POST /mcp/{agent_type}         — scoped to one agent type
GET  /mcp/{agent_type}/config  — ready-to-paste Claude Desktop config snippet

Tool naming convention: {agent_type}__{skill_name}
  e.g.  customer_service__analyze_sentiment

Multi-worker note
-----------------
Session tracking uses Redis when REDIS_URL is set. Without it, the
Mcp-Session-Id → session mapping lives in process memory — tool execution
still works correctly across workers, only trace IDs are lost.
"""

import json
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from registry import get_registry
from session import get_tracker

logger = structlog.get_logger()
router = APIRouter()

MCP_VERSION = "2025-03-26"
TOOL_SEP = "__"

_DispatchResult = tuple[Dict[str, Any], Optional[str], Optional[str]]


# ── JSON-RPC helpers ──────────────────────────────────────────────────────────

def _ok(id_: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result, "id": id_}


def _err(id_: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": id_}


# ── Tool catalogue ────────────────────────────────────────────────────────────

def _build_tools(agent_type: Optional[str]) -> List[Dict[str, Any]]:
    registry = get_registry()
    tools = []
    types = [agent_type] if agent_type else registry.list_agent_types()
    for at in types:
        for skill_name in registry.list_skills(at):
            fn = registry.get(at, skill_name)
            schema = registry.get_schema(at, skill_name)
            tools.append({
                "name": f"{at}{TOOL_SEP}{skill_name}",
                "description": (fn.__doc__ or "").strip().splitlines()[0],
                "inputSchema": schema,
            })
    return tools


# ── Request dispatch ──────────────────────────────────────────────────────────

async def _dispatch(
    body: Dict[str, Any],
    agent_type: Optional[str],
    company_id: str,
    mcp_session_id: Optional[str],
) -> "_DispatchResult":
    method: str = body.get("method", "")
    params: Dict[str, Any] = body.get("params", {})
    id_: Any = body.get("id")

    if method.startswith("notifications/"):
        return {}, None, None

    if method == "ping":
        return _ok(id_, {}), None, None

    # ── initialize ────────────────────────────────────────────────────────────
    if method == "initialize":
        mcp_sid, trace_id = await get_tracker().create(
            agent_type=agent_type,
            client_info=params.get("clientInfo", {}),
            protocol_version=params.get("protocolVersion"),
        )
        return (
            _ok(id_, {
                "protocolVersion": MCP_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "MCPCloud", "version": "0.1.0"},
            }),
            mcp_sid,
            trace_id,
        )

    # ── tools/list ────────────────────────────────────────────────────────────
    if method == "tools/list":
        return _ok(id_, {"tools": _build_tools(agent_type)}), None, None

    # ── tools/call ────────────────────────────────────────────────────────────
    if method == "tools/call":
        tool_name: str = params.get("name", "")
        arguments: Dict[str, Any] = params.get("arguments", {})

        if TOOL_SEP not in tool_name:
            return _err(id_, -32602, f"Invalid tool name '{tool_name}': expected <agent_type>{TOOL_SEP}<skill>"), None, None

        at, skill_name = tool_name.split(TOOL_SEP, 1)

        if agent_type and at != agent_type:
            return _err(id_, -32602, f"Tool '{tool_name}' not available in scope '{agent_type}'"), None, None

        fn = get_registry().get(at, skill_name)
        if fn is None:
            return _err(id_, -32602, f"Tool '{tool_name}' not found"), None, None

        entry = await get_tracker().get(mcp_session_id) if mcp_session_id else None
        trace_id = entry["trace_id"] if entry else None

        logger.info("Tool call", tool=tool_name, trace_id=trace_id, company_id=company_id)

        try:
            result = await fn(arguments, {"company_id": company_id, "trace_id": trace_id})
            content_text = json.dumps(result.output) if result.success else (result.error or "Skill failed")
            is_error = not result.success
        except Exception as exc:
            logger.error("Skill execution error", tool=tool_name, error=str(exc), exc_info=True)
            content_text = str(exc)
            is_error = True

        logger.info("Tool result", tool=tool_name, success=not is_error, trace_id=trace_id)

        return (
            _ok(id_, {
                "content": [{"type": "text", "text": content_text}],
                "isError": is_error,
            }),
            None,
            None,
        )

    return _err(id_, -32601, f"Method not found: {method}"), None, None


# ── Shared request handler ────────────────────────────────────────────────────

async def _handle(request: Request, agent_type: Optional[str]) -> Response:
    company_id = request.headers.get("X-Company-ID", "default")
    mcp_session_id = request.headers.get("Mcp-Session-Id")

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(_err(None, -32700, "Parse error: invalid JSON"), status_code=400)

    resp_body, new_sid, new_trace_id = await _dispatch(body, agent_type, company_id, mcp_session_id)

    if not resp_body:
        return Response(status_code=202)

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if new_sid:
        headers["Mcp-Session-Id"] = new_sid
    if new_trace_id:
        headers["X-Trace-ID"] = new_trace_id

    return JSONResponse(resp_body, headers=headers)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("", summary="MCP endpoint — all agent types")
async def mcp_all(request: Request) -> Response:
    return await _handle(request, agent_type=None)


@router.post("/{agent_type}", summary="MCP endpoint — scoped to one agent type")
async def mcp_scoped(request: Request, agent_type: str) -> Response:
    return await _handle(request, agent_type=agent_type)


@router.get(
    "/{agent_type}/config",
    summary="Claude Desktop / MCP client config snippet",
    response_model=Dict[str, Any],
)
async def mcp_config(request: Request, agent_type: str) -> Dict[str, Any]:
    """Returns a ready-to-paste snippet for claude_desktop_config.json."""
    base = str(request.base_url).rstrip("/")
    return {
        "mcpServers": {
            agent_type: {
                "url": f"{base}/mcp/{agent_type}",
                "transport": "http",
            }
        }
    }
