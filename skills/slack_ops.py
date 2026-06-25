"""Slack Operations — send messages and alerts to Slack channels.

To connect to a real Slack workspace, set in .env:
    SLACK_WEBHOOK_URL = https://hooks.slack.com/services/T.../B.../...

Create a webhook at: api.slack.com/apps → Incoming Webhooks → Add New Webhook

Without this, skills log the message locally and return stub data so
you can develop workflows before wiring up credentials.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from registry import SkillResult, get_registry

_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
_CONFIGURED = bool(_WEBHOOK)

logger = logging.getLogger(__name__)


def _build_blocks(
    text: str,
    title: Optional[str],
    fields: Optional[List[Dict[str, str]]],
    urgent: bool,
) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []

    if title:
        prefix = ":rotating_light: " if urgent else ":speech_balloon: "
        blocks.append({
            "type": "header",
            "text": {"type": "plain_text", "text": f"{prefix}{title}"},
        })

    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    })

    if fields:
        blocks.append({
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*{f['label']}*\n{f['value']}"}
                for f in fields
            ],
        })

    return blocks


async def send_message(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Send a message to a Slack channel via an incoming webhook.

    Input: { "text": "Deploy complete on prod",
             "title": "Release v2.1",
             "channel": "#deployments",
             "fields": [{"label": "Version", "value": "v2.1"},
                        {"label": "Status",  "value": "✅ Success"}] }
    """
    text    = input.get("text", "").strip()
    title   = input.get("title")
    channel = input.get("channel")
    fields  = input.get("fields")

    if not text:
        return SkillResult(success=False, output={}, error="'text' is required")

    payload: Dict[str, Any] = {
        "text":   title or text,
        "blocks": _build_blocks(text, title, fields, urgent=False),
    }
    if channel:
        payload["channel"] = channel

    if _CONFIGURED:
        # ── Real Slack call ───────────────────────────────────────────────────
        async with httpx.AsyncClient() as client:
            resp = await client.post(_WEBHOOK, json=payload, timeout=10)
            resp.raise_for_status()
            return SkillResult(success=True, output={
                "sent": True,
                "channel": channel or "default webhook channel",
                "text": text,
            })
        # ─────────────────────────────────────────────────────────────────────

    # Stub — logs to console, no HTTP call
    logger.info("[slack_ops stub] channel=%s | %s", channel or "webhook", text)
    return SkillResult(success=True, output={
        "sent":    True,
        "channel": channel or "default webhook channel",
        "text":    text,
        "_stub":   True,
    })


async def alert(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Send an urgent @channel alert to Slack with a severity badge.

    Input: { "text": "Database CPU at 98%",
             "title": "Production Alert",
             "severity": "critical|warning|info",
             "fields": [{"label": "Service", "value": "postgres-primary"}] }
    """
    text     = input.get("text", "").strip()
    title    = input.get("title", "Alert")
    severity = input.get("severity", "warning").lower()
    channel  = input.get("channel")
    fields   = input.get("fields")

    if not text:
        return SkillResult(success=False, output={}, error="'text' is required")

    severity_prefix = {
        "critical": ":red_circle: *CRITICAL*",
        "warning":  ":large_yellow_circle: *WARNING*",
        "info":     ":large_blue_circle: *INFO*",
    }.get(severity, ":large_yellow_circle: *WARNING*")

    full_text = f"{severity_prefix}\n{text}"
    if severity == "critical":
        full_text = f"<!channel> {full_text}"

    payload: Dict[str, Any] = {
        "text":   f"[{severity.upper()}] {title}",
        "blocks": _build_blocks(full_text, title, fields, urgent=severity == "critical"),
    }
    if channel:
        payload["channel"] = channel

    if _CONFIGURED:
        # ── Real Slack call ───────────────────────────────────────────────────
        async with httpx.AsyncClient() as client:
            resp = await client.post(_WEBHOOK, json=payload, timeout=10)
            resp.raise_for_status()
            return SkillResult(success=True, output={
                "sent":     True,
                "severity": severity,
                "channel":  channel or "default webhook channel",
                "text":     text,
            })
        # ─────────────────────────────────────────────────────────────────────

    # Stub
    logger.warning("[slack_ops stub] ALERT severity=%s | %s", severity, text)
    return SkillResult(success=True, output={
        "sent":     True,
        "severity": severity,
        "channel":  channel or "default webhook channel",
        "text":     text,
        "_stub":    True,
    })


def register_all() -> None:
    registry = get_registry()

    registry.register(
        "slack_ops", "send_message", send_message,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text":    {"type": "string", "description": "Message body (Markdown supported)."},
                "title":   {"type": "string", "description": "Optional bold header above the message."},
                "channel": {"type": "string", "description": "Override channel, e.g. #deployments. Defaults to webhook channel."},
                "fields":  {
                    "type": "array",
                    "description": "Key-value pairs shown as a two-column grid below the message.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "string"},
                        },
                    },
                },
            },
        },
    )

    registry.register(
        "slack_ops", "alert", alert,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text":     {"type": "string", "description": "Alert message body."},
                "title":    {"type": "string", "description": "Alert title."},
                "severity": {"type": "string", "enum": ["critical", "warning", "info"], "description": "Severity level. Critical sends @channel."},
                "channel":  {"type": "string", "description": "Override channel."},
                "fields":   {
                    "type": "array",
                    "description": "Structured context fields, e.g. Service, Region, Value.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "string"},
                        },
                    },
                },
            },
        },
    )
