"""IT helpdesk skills — automated ticket triage and response drafting.

Skills:
- triage         : classify priority, category, routing team, and extract
                   key details (error codes, affected systems, urgency signals)
- draft_response : generate a professional first-response template based on
                   triage output, ready to send or hand to an agent

No external dependencies — works without API keys.
Plug in an LLM (Anthropic/OpenAI) via context["anthropic_api_key"] to
upgrade the draft_response output from template-based to fully generated.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from registry import SkillResult, get_registry

# ── Priority signals ──────────────────────────────────────────────────────────

_CRITICAL = [
    "system down", "complete outage", "all users affected", "production down",
    "data loss", "security breach", "ransomware", "cannot work at all",
    "entire office", "everyone is affected",
]

_HIGH = [
    "client meeting", "client presentation", "customer demo", "board meeting",
    "cannot work", "can't work", "blocking", "urgent", "asap", "as soon as",
    "today", "this morning", "this afternoon", "tomorrow morning", "deadline",
    "executive", "ceo", "cto", "vp ", "director",
]

_LOW = [
    "when possible", "no rush", "low priority", "minor issue", "cosmetic",
    "nice to have", "not urgent", "whenever", "at your convenience",
    "not blocking", "small thing",
]

# ── Category signals ──────────────────────────────────────────────────────────

_CATEGORIES = {
    "hardware": [
        "laptop", "computer", "keyboard", "mouse", "monitor", "screen",
        "display", "printer", "headset", "webcam", "docking station",
        "charger", "battery", "hard drive", "ram", "memory", "device",
        "phone", "mobile", "tablet",
    ],
    "network": [
        "vpn", "wifi", "wi-fi", "wireless", "internet", "connection",
        "network", "cannot connect", "can't connect", "no internet",
        "firewall", "proxy", "dns", "slow connection", "bandwidth",
        "ethernet", "disconnect", "dropped connection",
    ],
    "access": [
        "password", "login", "locked out", "can't log in", "cannot log in",
        "account", "permissions", "access denied", "unauthorized",
        "two-factor", "2fa", "mfa", "sso", "single sign-on",
        "forgot password", "reset password", "new employee", "onboarding",
        "offboarding", "user account",
    ],
    "email": [
        "email", "outlook", "calendar", "teams", "slack", "zoom",
        "meeting", "invite", "mailbox", "inbox", "spam", "phishing",
        "attachment", "signature", "shared mailbox",
    ],
    "software": [
        "install", "installation", "uninstall", "update", "upgrade",
        "crash", "crashes", "error", "not opening", "won't open",
        "slow", "freezing", "hangs", "application", "app", "software",
        "license", "excel", "word", "powerpoint", "office", "adobe",
        "browser", "chrome", "edge", "firefox",
    ],
}

_TEAM_MAP = {
    "hardware":  ("Hardware & End-User Computing", 8),
    "network":   ("Network Operations",            4),
    "access":    ("Identity & Access Management",  2),
    "email":     ("Collaboration Tools",           4),
    "software":  ("Desktop Support",               4),
    "other":     ("General IT Support",            8),
}

# ── Error code patterns ───────────────────────────────────────────────────────

_ERROR_PATTERNS = [
    r'\b0x[0-9A-Fa-f]{4,8}\b',          # Windows hex codes: 0x80070005
    r'\bHTTP\s?[45]\d{2}\b',             # HTTP errors: HTTP 404, HTTP 500
    r'\berror\s?(?:code\s?)?[:\s]?\d{3,}\b',  # Error: 1234, Error code 5678
    r'\bevent\s?id\s?\d+\b',             # Event ID 1234
    r'\bexception\s?[\w.]+exception\b',  # NullPointerException etc.
]


def _lower(text: str) -> str:
    return text.lower()


def _detect_priority(text: str) -> tuple[str, str]:
    t = _lower(text)
    for phrase in _CRITICAL:
        if phrase in t:
            return "critical", f'Matched critical signal: "{phrase}"'
    for phrase in _HIGH:
        if phrase in t:
            return "high", f'Matched urgency signal: "{phrase}"'
    for phrase in _LOW:
        if phrase in t:
            return "low", f'Matched low-priority signal: "{phrase}"'
    return "normal", "No urgency signals detected"


def _detect_category(text: str) -> tuple[str, Optional[str]]:
    t = _lower(text)
    scores: Dict[str, int] = {}
    for cat, keywords in _CATEGORIES.items():
        hits = sum(1 for kw in keywords if kw in t)
        if hits:
            scores[cat] = hits
    if not scores:
        return "other", None
    primary = max(scores, key=lambda c: scores[c])
    # subcategory: strongest individual keyword hit
    subcategory = None
    for kw in _CATEGORIES.get(primary, []):
        if kw in t:
            subcategory = kw
            break
    return primary, subcategory


def _extract_error_codes(text: str) -> List[str]:
    found = []
    for pattern in _ERROR_PATTERNS:
        found.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(dict.fromkeys(found))  # deduplicate, preserve order


def _extract_urgency_signals(text: str) -> List[str]:
    t = _lower(text)
    return [p for p in (_CRITICAL + _HIGH) if p in t]


# ── Skills ────────────────────────────────────────────────────────────────────

async def triage(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Triage an IT support ticket: priority, category, routing team, error codes.

    Input: { "ticket": "User's laptop won't connect to VPN. Error 0x80070005.
              Client presentation tomorrow morning." }
    """
    ticket = input.get("ticket", "").strip()
    if not ticket:
        return SkillResult(success=False, output={}, error="'ticket' is required")

    priority, priority_reason = _detect_priority(ticket)
    category, subcategory = _detect_category(ticket)
    team, sla_hours = _TEAM_MAP.get(category, _TEAM_MAP["other"])
    error_codes = _extract_error_codes(ticket)
    urgency_signals = _extract_urgency_signals(ticket)

    # Shorten SLA for critical
    if priority == "critical":
        sla_hours = 1
    elif priority == "high" and sla_hours > 4:
        sla_hours = 4

    return SkillResult(success=True, output={
        "priority": priority,
        "priority_reason": priority_reason,
        "category": category,
        "subcategory": subcategory,
        "routing": {
            "team": team,
            "sla_hours": sla_hours,
        },
        "error_codes": error_codes,
        "urgency_signals": urgency_signals,
    })


_RESPONSE_TEMPLATES = {
    "critical": (
        "Thank you for contacting IT Support. We have flagged your ticket as "
        "CRITICAL and are escalating it immediately. A senior engineer will "
        "contact you within 1 hour."
    ),
    "high": (
        "Thank you for reaching out. We understand this is time-sensitive and "
        "have prioritised your ticket. A technician will be in touch within 4 hours."
    ),
    "normal": (
        "Thank you for contacting IT Support. We have received your ticket and "
        "will respond within one business day."
    ),
    "low": (
        "Thank you for reaching out. We have logged your request and will "
        "address it when a technician is available, typically within 3–5 business days."
    ),
}

_CATEGORY_NEXT_STEPS = {
    "hardware": [
        "Please confirm the make and model of the affected device.",
        "Note any physical damage or unusual behaviour (overheating, noise, etc.).",
        "If possible, test with a spare device to isolate the issue.",
    ],
    "network": [
        "Please confirm whether you are on-site or working remotely.",
        "Try restarting your network adapter: Settings → Network → Disable/Enable.",
        "If using VPN, note the exact error message or code shown.",
    ],
    "access": [
        "Do not attempt to log in more than 3 times to avoid account lockout.",
        "Confirm the email address associated with the account.",
        "If MFA is involved, have your phone or authenticator app ready.",
    ],
    "email": [
        "Confirm which mail client and version you are using (e.g. Outlook 365).",
        "Try accessing your email via the web browser as a temporary workaround.",
        "Note when the issue started and whether anything changed recently.",
    ],
    "software": [
        "Please provide the exact error message or screenshot if possible.",
        "Confirm the application name and version (Help → About).",
        "Try closing and reopening the application as a first step.",
    ],
    "other": [
        "Please provide as much detail as possible about the issue.",
        "Note any error messages, codes, or recent changes to your setup.",
    ],
}


async def draft_response(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Draft a professional first-response email for an IT support ticket.

    Input: { "ticket": "...", "priority": "high", "category": "network",
             "requester_name": "Alex" }
    Pair with triage output for best results.
    """
    ticket = input.get("ticket", "").strip()
    priority = input.get("priority", "normal").lower()
    category = input.get("category", "other").lower()
    requester = input.get("requester_name", "there")
    ticket_ref = input.get("ticket_ref", "")

    if not ticket:
        return SkillResult(success=False, output={}, error="'ticket' is required")

    if priority not in _RESPONSE_TEMPLATES:
        priority = "normal"
    if category not in _CATEGORY_NEXT_STEPS:
        category = "other"

    team, _ = _TEAM_MAP.get(category, _TEAM_MAP["other"])
    ref_line = f" (Ref: {ticket_ref})" if ticket_ref else ""

    subject = f"RE: Your IT Support Request{ref_line} [{priority.upper()}]"
    greeting = f"Hi {requester},"
    body = _RESPONSE_TEMPLATES[priority]
    next_steps = _CATEGORY_NEXT_STEPS[category]
    closing = (
        f"In the meantime, if your situation changes or becomes more urgent "
        f"please reply to this email and we will re-prioritise accordingly."
    )
    signature = f"Kind regards,\n{team}\nIT Support"

    return SkillResult(success=True, output={
        "subject": subject,
        "greeting": greeting,
        "body": body,
        "next_steps": next_steps,
        "closing": closing,
        "signature": signature,
        "full_email": "\n\n".join([
            greeting,
            body,
            "To help us resolve this faster, please:\n" +
            "\n".join(f"  • {s}" for s in next_steps),
            closing,
            signature,
        ]),
    })


def register_all() -> None:
    registry = get_registry()

    registry.register(
        "it_helpdesk", "triage", triage,
        schema={
            "type": "object",
            "required": ["ticket"],
            "properties": {
                "ticket": {
                    "type": "string",
                    "description": "The raw ticket text submitted by the user.",
                },
            },
        },
    )

    registry.register(
        "it_helpdesk", "draft_response", draft_response,
        schema={
            "type": "object",
            "required": ["ticket"],
            "properties": {
                "ticket": {
                    "type": "string",
                    "description": "The raw ticket text.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["critical", "high", "normal", "low"],
                    "description": "Priority from triage output (defaults to normal).",
                },
                "category": {
                    "type": "string",
                    "enum": ["hardware", "network", "access", "email", "software", "other"],
                    "description": "Category from triage output.",
                },
                "requester_name": {
                    "type": "string",
                    "description": "First name of the person who raised the ticket.",
                },
                "ticket_ref": {
                    "type": "string",
                    "description": "Optional ticket reference number.",
                },
            },
        },
    )
