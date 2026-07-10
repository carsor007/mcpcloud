"""Tool browser UI — served at /ui."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MCPCloud · Tool Browser</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #222636;
    --border: #2e3248;
    --accent: #6c63ff;
    --accent-dim: #3d3880;
    --text: #e2e4f0;
    --text-dim: #7c82a8;
    --green: #4ade80;
    --red: #f87171;
    --yellow: #fbbf24;
    --mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
  }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: var(--text);
    cursor: pointer;
    user-select: none;
  }
  .logo span { color: var(--accent); }

  .badge {
    background: var(--accent-dim);
    color: var(--accent);
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.3px;
  }

  .header-right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .guide-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--text-dim);
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
  }
  .guide-btn:hover { border-color: var(--accent); color: var(--accent); }

  .status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-dim);
  }

  .dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--text-dim);
  }

  .layout {
    display: flex;
    height: calc(100vh - 53px);
    overflow: hidden;
  }

  /* Sidebar */
  .sidebar {
    width: 260px;
    flex-shrink: 0;
    min-height: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 12px 0;
  }

  .sidebar-section {
    padding: 8px 16px 2px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text-dim);
  }

  .tool-item {
    padding: 8px 16px;
    cursor: pointer;
    border-left: 3px solid transparent;
    transition: background 0.1s, border-color 0.1s;
  }
  .tool-item:hover { background: var(--surface2); }
  .tool-item.active { background: var(--surface2); border-left-color: var(--accent); }

  .tool-name {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .tool-desc {
    font-size: 11px;
    color: var(--text-dim);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 1px;
  }

  .empty-sidebar {
    padding: 20px 16px;
    font-size: 12px;
    color: var(--text-dim);
    line-height: 1.7;
  }

  .agent-group { margin-top: 6px; }

  /* Main panel */
  .main {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 24px;
  }

  .main > * + * { margin-top: 20px; }

  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }

  .card-header {
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
  }

  .card-body { padding: 16px 18px; }

  /* Guide styles */
  .guide-intro {
    font-size: 13px;
    color: var(--text-dim);
    line-height: 1.7;
  }

  .guide-intro strong { color: var(--text); }

  .guide-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }

  @media (max-width: 900px) { .guide-grid { grid-template-columns: 1fr; } }

  .guide-tile {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .guide-tile-icon { font-size: 22px; }

  .guide-tile-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
  }

  .guide-tile-body {
    font-size: 12px;
    color: var(--text-dim);
    line-height: 1.6;
  }

  .guide-tile-body code {
    font-family: var(--mono);
    font-size: 11px;
    background: var(--bg);
    padding: 1px 5px;
    border-radius: 3px;
    color: var(--accent);
  }

  /* Steps */
  .steps { display: flex; flex-direction: column; gap: 0; }

  .step {
    display: flex;
    gap: 14px;
    position: relative;
  }

  .step:not(:last-child)::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 32px;
    bottom: -4px;
    width: 1px;
    background: var(--border);
  }

  .step-num {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--accent-dim);
    color: var(--accent);
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
    z-index: 1;
  }

  .step-content { padding-bottom: 20px; flex: 1; }

  .step-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 4px;
  }

  .step-body {
    font-size: 12px;
    color: var(--text-dim);
    line-height: 1.7;
  }

  .step-body code {
    font-family: var(--mono);
    font-size: 11px;
    background: var(--bg);
    padding: 1px 5px;
    border-radius: 3px;
    color: var(--accent);
  }

  /* Code blocks */
  .code-wrap { position: relative; margin-top: 10px; }

  .code-block {
    font-family: var(--mono);
    font-size: 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 14px 14px 14px;
    color: #a9b1d6;
    white-space: pre;
    overflow-x: auto;
    line-height: 1.6;
  }

  .copy-btn {
    position: absolute;
    top: 8px; right: 8px;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text-dim);
    border-radius: 4px;
    padding: 3px 9px;
    font-size: 11px;
    cursor: pointer;
    transition: color 0.15s, border-color 0.15s;
  }
  .copy-btn:hover { color: var(--text); border-color: var(--accent); }

  /* Tool detail */
  .tool-full-name {
    font-family: var(--mono);
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
  }
  .tool-full-desc { color: var(--text-dim); font-size: 13px; margin-top: 4px; }

  .schema-block {
    font-family: var(--mono);
    font-size: 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 14px;
    color: #a9b1d6;
    white-space: pre;
    overflow-x: auto;
    line-height: 1.5;
  }

  textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 12px;
    padding: 12px 14px;
    resize: vertical;
    min-height: 120px;
    outline: none;
    transition: border-color 0.15s;
    line-height: 1.5;
  }
  textarea:focus { border-color: var(--accent); }

  button.run-btn {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
    display: flex;
    align-items: center;
    gap: 7px;
  }
  button.run-btn:hover { opacity: 0.88; }
  button.run-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .result-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
  }
  .result-header.ok { color: var(--green); }
  .result-header.err { color: var(--red); }

  .result-body {
    font-family: var(--mono);
    font-size: 12px;
    padding: 14px 18px;
    white-space: pre;
    overflow-x: auto;
    line-height: 1.5;
    color: #a9b1d6;
  }

  .spinner {
    display: inline-block;
    width: 14px; height: 14px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  label.input-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: block;
    margin-bottom: 6px;
  }

  .input-hint { font-size: 11px; color: var(--text-dim); margin-top: 6px; }

  .tag {
    display: inline-block;
    font-family: var(--mono);
    font-size: 10px;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text-dim);
    padding: 1px 7px;
    border-radius: 4px;
  }
</style>
</head>
<body>

<header>
  <div class="logo" onclick="showGuide()">MCP<span>Cloud</span></div>
  <div class="badge">Tool Browser</div>
  <div class="header-right">
    <a href="/ui/skills" class="guide-btn" style="text-decoration:none">+ Skill Editor</a>
    <a href="/ui/audit" class="guide-btn" style="text-decoration:none">Audit Log</a>
    <button class="guide-btn" onclick="showGuide()">? Guide</button>
    <div class="status">
      <div class="dot" id="status-dot"></div>
      <span id="status-text">connecting…</span>
    </div>
  </div>
</header>

<div class="layout">
  <nav class="sidebar" id="sidebar">
    <div class="empty-sidebar">Loading…</div>
  </nav>
  <main class="main" id="main"></main>
</div>

<script>
const $ = id => document.getElementById(id)
const origin = window.location.origin

let allTools = []
let activeToolName = null

// ── Skill file template ───────────────────────────────────────────────────────
const SKILL_TEMPLATE = `# skills/servicenow_ops.py
import os, httpx
from registry import SkillResult, get_registry

# Credentials loaded from .env at startup — never hard-coded
_BASE = os.getenv("SNOW_URL", "")    # https://company.service-now.com
_AUTH = (os.getenv("SNOW_USER", ""), os.getenv("SNOW_PASS", ""))

async def get_incident(input: dict, context: dict) -> SkillResult:
    \'\'\'Fetch a ServiceNow incident by number and return its state and priority.\'\'\'
    number = input.get("number", "")
    async with httpx.AsyncClient() as c:
        r = await c.get(
            f"{_BASE}/api/now/table/incident",
            auth=_AUTH,
            params={"sysparm_query": f"number={number}",
                    "sysparm_fields": "number,short_description,state,priority,assigned_to"},
            timeout=10,
        )
        r.raise_for_status()
        items = r.json().get("result", [])
    if not items:
        return SkillResult(success=False, output={}, error=f"{number} not found")
    inc = items[0]
    return SkillResult(success=True, output={
        "number":      inc["number"],
        "summary":     inc["short_description"],
        "state":       inc["state"],
        "priority":    inc["priority"],
        "assigned_to": inc.get("assigned_to", {}).get("display_value", "Unassigned"),
    })

def register_all():
    get_registry().register(
        "servicenow",       # agent type  →  groups skills in the sidebar
        "get_incident",     # skill name  →  shown under the group
        get_incident,
        schema={
            "type": "object",
            "required": ["number"],
            "properties": {
                "number": {"type": "string", "description": "Incident number, e.g. INC0012345"}
            }
        }
    )`

// ── Auth pattern snippets ─────────────────────────────────────────────────────
const AUTH_BEARER = `# .env
ACME_API_TOKEN=sk-your-token-here

# skills/acme_ops.py
import os, httpx
from registry import SkillResult, get_registry

_TOKEN = os.getenv("ACME_API_TOKEN", "")

async def list_items(input: dict, context: dict) -> SkillResult:
    \'\'\'List items from the Acme API.\'\'\'
    async with httpx.AsyncClient() as c:
        r = await c.get(
            "https://api.acme.com/v1/items",
            headers={"Authorization": f"Bearer {_TOKEN}"},
            timeout=10,
        )
        r.raise_for_status()
    return SkillResult(success=True, output=r.json())`

const AUTH_EMAIL_TOKEN = `# .env  —  Jira / Atlassian
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=svc-mcpcloud@company.com   # service account email
JIRA_API_TOKEN=ATATT...               # id.atlassian.com → Security → API tokens

# skills/jira_ops.py
import os, httpx

_URL  = os.getenv("JIRA_URL", "")
_AUTH = (os.getenv("JIRA_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))

# HTTP Basic auth — Atlassian accepts email:api_token as the credential pair
async with httpx.AsyncClient() as c:
    r = await c.post(f"{_URL}/rest/api/2/issue", auth=_AUTH, json={...})`

const AUTH_SERVICE_ACCOUNT = `# .env  —  ServiceNow / SAP / internal APIs
SNOW_URL=https://company.service-now.com
SNOW_USER=svc-mcpcloud       # dedicated service account, not a personal login
SNOW_PASS=strong-random-password

# skills/servicenow_ops.py
import os, httpx

_BASE = os.getenv("SNOW_URL", "")
_AUTH = (os.getenv("SNOW_USER", ""), os.getenv("SNOW_PASS", ""))

async with httpx.AsyncClient() as c:
    r = await c.get(f"{_BASE}/api/now/table/incident", auth=_AUTH, params={...})

# Same pattern works for SAP, Oracle, and most internal REST APIs.
# On AWS: store credentials in Secrets Manager and inject via ECS task definition.
# The skill code is identical — os.getenv() works the same either way.`

const CLAUDE_CONFIG = () => `// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "servicenow": {
      "url": "${origin}/mcp/servicenow",
      "transport": "http"
    }
  }
}`

// ── Guide view ────────────────────────────────────────────────────────────────
function showGuide() {
  if (activeToolName) {
    const prev = document.getElementById('item-' + CSS.escape(activeToolName))
    if (prev) prev.classList.remove('active')
    activeToolName = null
  }

  $('main').innerHTML = `
    <div class="card">
      <div class="card-header"><div class="card-title">What is MCPCloud?</div></div>
      <div class="card-body">
        <p class="guide-intro">
          <strong>MCPCloud</strong> is a self-hosted MCP (Model Context Protocol) gateway.
          Write any Python function, register it as a skill, and it instantly becomes
          a tool that Claude Desktop, Claude API, Cursor, or any MCP client can call —
          no infrastructure changes, no vendor lock-in.
        </p>
        <div style="margin-top:18px" class="guide-grid">
          <div class="guide-tile">
            <div class="guide-tile-icon">📁</div>
            <div class="guide-tile-title">Sidebar — Agent types</div>
            <div class="guide-tile-body">
              The left panel groups skills by <strong>agent type</strong> — the first part of a tool name like
              <code>example</code> in <code>example__echo</code>.
              Each file in <code>skills/</code> defines one agent type and its skills.
            </div>
          </div>
          <div class="guide-tile">
            <div class="guide-tile-icon">🔧</div>
            <div class="guide-tile-title">Tools — Skills</div>
            <div class="guide-tile-body">
              Each item under an agent type is a <strong>skill</strong> — an async Python function.
              Click one to see its input schema and call it live.
              Tool names follow the pattern <code>agent_type__skill_name</code>.
            </div>
          </div>
          <div class="guide-tile">
            <div class="guide-tile-icon">⚡</div>
            <div class="guide-tile-title">Redis — Multi-worker</div>
            <div class="guide-tile-body">
              Session tracking uses Redis when <code>REDIS_URL</code> is set (included in Docker Compose).
              Without it, an in-process dict is used — fine for local dev and single-worker deploys.
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title">How to add a skill</div></div>
      <div class="card-body">
        <div class="steps">
          <div class="step">
            <div class="step-num">1</div>
            <div class="step-content">
              <div class="step-title">Create a file in <code>skills/</code></div>
              <div class="step-body">
                Drop any <code>.py</code> file into the <code>skills/</code> directory.
                The gateway auto-discovers it on startup — no config changes needed.
              </div>
              <div class="code-wrap">
                <div class="code-block" id="cb-skill">${escHtml(SKILL_TEMPLATE)}</div>
                <button class="copy-btn" onclick="copy('cb-skill', this)">Copy</button>
              </div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <div class="step-content">
              <div class="step-title">Restart the server</div>
              <div class="step-body">
                Skills are loaded at startup. In Docker: <code>docker compose restart mcp</code>.
                In dev with <code>HOT_RELOAD=true</code>: the server reloads automatically.
              </div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <div class="step-content">
              <div class="step-title">Your skill appears in this UI</div>
              <div class="step-body">
                Refresh this page. The new agent type and skill will appear in the sidebar.
                Click it to see the schema and test it live.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title">Credentials &amp; auth patterns</div></div>
      <div class="card-body">
        <p class="guide-intro" style="margin-bottom:18px">
          Store all secrets in <strong>.env</strong> and read them with <code>os.getenv()</code>
          at module load time. Three patterns cover the vast majority of enterprise and SaaS APIs.
        </p>

        <div style="margin-bottom:20px">
          <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px">Pattern 1 — Bearer token</div>
          <div style="font-size:12px;color:var(--text-dim);margin-bottom:8px">
            Slack, Linear, Notion, GitHub, and most modern REST APIs. One token, passed in the <code>Authorization</code> header.
          </div>
          <div class="code-wrap">
            <div class="code-block" id="cb-auth1">${escHtml(AUTH_BEARER)}</div>
            <button class="copy-btn" onclick="copy('cb-auth1', this)">Copy</button>
          </div>
        </div>

        <div style="margin-bottom:20px">
          <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px">Pattern 2 — Email + API token</div>
          <div style="font-size:12px;color:var(--text-dim);margin-bottom:8px">
            Jira, Confluence, and other Atlassian tools. HTTP Basic auth using a service account email paired with an API token (not a password).
          </div>
          <div class="code-wrap">
            <div class="code-block" id="cb-auth2">${escHtml(AUTH_EMAIL_TOKEN)}</div>
            <button class="copy-btn" onclick="copy('cb-auth2', this)">Copy</button>
          </div>
        </div>

        <div style="margin-bottom:4px">
          <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px">Pattern 3 — Service account (username + password)</div>
          <div style="font-size:12px;color:var(--text-dim);margin-bottom:8px">
            ServiceNow, SAP, Oracle, and internal APIs. Use a dedicated service account — not a personal login — so access survives staff changes and can be audited independently.
          </div>
          <div class="code-wrap">
            <div class="code-block" id="cb-auth3">${escHtml(AUTH_SERVICE_ACCOUNT)}</div>
            <button class="copy-btn" onclick="copy('cb-auth3', this)">Copy</button>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title">Connect an MCP client</div></div>
      <div class="card-body">
        <div class="steps">
          <div class="step">
            <div class="step-num">1</div>
            <div class="step-content">
              <div class="step-title">Get the config snippet from the API</div>
              <div class="step-body">
                Each agent type has a ready-to-paste config endpoint:<br>
                <code>GET /mcp/{agent_type}/config</code><br><br>
                For example: <code>GET ${origin}/mcp/servicenow/config</code>
              </div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <div class="step-content">
              <div class="step-title">Add it to Claude Desktop</div>
              <div class="step-body">
                Paste the returned object into <code>claude_desktop_config.json</code>
                under <code>"mcpServers"</code>. Restart Claude Desktop.
              </div>
              <div class="code-wrap">
                <div class="code-block" id="cb-claude">${escHtml(CLAUDE_CONFIG())}</div>
                <button class="copy-btn" onclick="copy('cb-claude', this)">Copy</button>
              </div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <div class="step-content">
              <div class="step-title">All tools available immediately</div>
              <div class="step-body">
                Claude can now call your registered skills as tools in any conversation.<br><br>
                Scope to one agent type: <code>${origin}/mcp/servicenow</code><br>
                Expose everything: <code>${origin}/mcp</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
}

// ── Fetch tools ───────────────────────────────────────────────────────────────
async function loadTools() {
  try {
    const res = await fetch('/mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/list', params: {} })
    })
    const data = await res.json()
    allTools = data.result?.tools || []
    renderSidebar(allTools)
    $('status-dot').style.background = 'var(--green)'
    $('status-dot').style.boxShadow = '0 0 6px var(--green)'
    $('status-text').textContent = `${allTools.length} tool${allTools.length !== 1 ? 's' : ''} registered`
  } catch (e) {
    $('status-dot').style.background = 'var(--red)'
    $('status-dot').style.boxShadow = '0 0 6px var(--red)'
    $('status-text').textContent = 'server unreachable'
    $('sidebar').innerHTML = '<div class="empty-sidebar">Could not connect to server.</div>'
  }
  showGuide()
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
function renderSidebar(tools) {
  if (!tools.length) {
    $('sidebar').innerHTML = '<div class="empty-sidebar">No skills registered yet.<br><br>Add a <code>.py</code> file to <code>skills/</code> — click <strong>? Guide</strong> to see how.</div>'
    return
  }

  const groups = {}
  tools.forEach(t => {
    const [agent] = t.name.split('__')
    if (!groups[agent]) groups[agent] = []
    groups[agent].push(t)
  })

  let html = ''
  for (const [agent, agentTools] of Object.entries(groups)) {
    html += `<div class="agent-group"><div class="sidebar-section">${agent}</div>`
    agentTools.forEach(t => {
      const skill = t.name.split('__')[1]
      html += `
        <div class="tool-item" id="item-${CSS.escape(t.name)}" onclick="selectTool('${t.name}')">
          <div class="tool-name">${skill}</div>
          <div class="tool-desc">${t.description || ''}</div>
        </div>`
    })
    html += '</div>'
  }
  $('sidebar').innerHTML = html
}

// ── Select tool ───────────────────────────────────────────────────────────────
function selectTool(name) {
  if (activeToolName) {
    const prev = document.getElementById('item-' + CSS.escape(activeToolName))
    if (prev) prev.classList.remove('active')
  }
  activeToolName = name
  const item = document.getElementById('item-' + CSS.escape(name))
  if (item) item.classList.add('active')

  const tool = allTools.find(t => t.name === name)
  if (!tool) return

  const schema = tool.inputSchema || {}
  const defaultInput = buildDefaultInput(schema)

  $('main').innerHTML = `
    <div class="card">
      <div class="card-header">
        <div>
          <div class="tool-full-name">${name}</div>
          <div class="tool-full-desc">${tool.description || 'No description provided.'}</div>
        </div>
        <span class="tag">${name.split('__')[0]}</span>
      </div>
      <div class="card-body">
        <label class="input-label">Input schema</label>
        <div class="schema-block">${JSON.stringify(schema, null, 2)}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title">Call tool</div>
      </div>
      <div class="card-body" style="display:flex;flex-direction:column;gap:12px">
        <div>
          <label class="input-label">Arguments (JSON)</label>
          <textarea id="input-json" spellcheck="false">${JSON.stringify(defaultInput, null, 2)}</textarea>
          <div class="input-hint">Edit the JSON above, then click Run.</div>
        </div>
        <div>
          <button class="run-btn" id="run-btn" onclick="runTool()">
            <span>▶ Run</span>
          </button>
        </div>
      </div>
    </div>

    <div class="card" id="result-card" style="display:none">
      <div class="result-header" id="result-header"></div>
      <div class="result-body" id="result-body"></div>
    </div>
  `
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function buildDefaultInput(schema) {
  if (!schema || !schema.properties) return {}
  const out = {}
  for (const [key, prop] of Object.entries(schema.properties)) {
    if (prop.type === 'string') out[key] = ''
    else if (prop.type === 'number' || prop.type === 'integer') out[key] = 0
    else if (prop.type === 'boolean') out[key] = false
    else if (prop.type === 'array') out[key] = []
    else out[key] = {}
  }
  return out
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}

function copy(blockId, btn) {
  const text = document.getElementById(blockId).textContent
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = 'Copied!'
    setTimeout(() => { btn.textContent = 'Copy' }, 1800)
  })
}

// ── Run tool ──────────────────────────────────────────────────────────────────
async function runTool() {
  const btn = $('run-btn')
  const resultCard = $('result-card')
  const resultHeader = $('result-header')
  const resultBody = $('result-body')

  let args
  try {
    args = JSON.parse($('input-json').value)
  } catch {
    resultCard.style.display = 'block'
    resultHeader.className = 'result-header err'
    resultHeader.innerHTML = '<span>✗</span> Invalid JSON in arguments'
    resultBody.textContent = 'Fix the JSON above and try again.'
    return
  }

  btn.disabled = true
  btn.innerHTML = '<span class="spinner"></span> Running…'

  try {
    const res = await fetch('/mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0', id: Date.now(),
        method: 'tools/call',
        params: { name: activeToolName, arguments: args }
      })
    })
    const data = await res.json()
    const toolResult = data.result
    const isError = toolResult?.isError ?? !!data.error
    const text = toolResult?.content?.[0]?.text ?? data.error?.message ?? JSON.stringify(data, null, 2)

    let pretty
    try { pretty = JSON.stringify(JSON.parse(text), null, 2) } catch { pretty = text }

    resultCard.style.display = 'block'
    resultHeader.className = `result-header ${isError ? 'err' : 'ok'}`
    resultHeader.innerHTML = isError ? '<span>✗</span> Error' : '<span>✓</span> Success'
    resultBody.textContent = pretty
  } catch (e) {
    resultCard.style.display = 'block'
    resultHeader.className = 'result-header err'
    resultHeader.innerHTML = '<span>✗</span> Request failed'
    resultBody.textContent = e.message
  } finally {
    btn.disabled = false
    btn.innerHTML = '<span>▶ Run</span>'
  }
}

loadTools()
</script>
</body>
</html>"""


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def tool_browser():
    return HTMLResponse(_HTML)


_SKILLS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MCPCloud · Skill Editor</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0f1117; --surface: #1a1d27; --surface2: #222636;
    --border: #2e3248; --accent: #6c63ff; --accent-dim: #3d3880;
    --text: #e2e4f0; --text-dim: #7c82a8;
    --green: #4ade80; --red: #f87171; --yellow: #fbbf24;
    --mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14px; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
  header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 14px 24px; display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
  .logo { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; color: var(--text); text-decoration: none; }
  .logo span { color: var(--accent); }
  .badge { background: var(--accent-dim); color: var(--accent); font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
  .header-right { margin-left: auto; display: flex; align-items: center; gap: 14px; }
  .nav-link { background: none; border: 1px solid var(--border); color: var(--text-dim); border-radius: 6px; padding: 5px 12px; font-size: 12px; font-weight: 500; cursor: pointer; text-decoration: none; transition: border-color 0.15s, color 0.15s; }
  .nav-link:hover { border-color: var(--accent); color: var(--accent); }

  .layout { display: flex; flex: 1; overflow: hidden; }

  /* Sidebar */
  .sidebar { width: 220px; flex-shrink: 0; background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .sidebar-header { padding: 12px 14px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }
  .sidebar-header span { font-size: 11px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; color: var(--text-dim); flex: 1; }
  .new-btn { background: var(--accent); color: #fff; border: none; border-radius: 5px; padding: 4px 10px; font-size: 11px; font-weight: 600; cursor: pointer; }
  .new-btn:hover { opacity: 0.88; }
  .skill-list { flex: 1; overflow-y: auto; padding: 8px 0; }
  .skill-group-label { padding: 10px 14px 3px; font-size: 10px; font-weight: 700; letter-spacing: 0.7px; text-transform: uppercase; color: var(--text-dim); }
  .skill-item { padding: 7px 14px; cursor: pointer; font-size: 13px; color: var(--text-dim); border-left: 2px solid transparent; transition: background 0.1s, color 0.1s; }
  .skill-item:hover { background: var(--surface2); color: var(--text); }
  .skill-item.active { background: var(--surface2); color: var(--accent); border-left-color: var(--accent); }
  .skill-item .loaded-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--green); margin-left: 6px; vertical-align: middle; }

  /* Editor area */
  .editor-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  .editor-toolbar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 10px 16px; display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
  .toolbar-field { display: flex; flex-direction: column; gap: 3px; }
  .toolbar-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-dim); }
  .toolbar-input { background: var(--surface2); border: 1px solid var(--border); color: var(--text); border-radius: 5px; padding: 5px 10px; font-size: 12px; font-family: var(--mono); width: 140px; }
  .toolbar-input:focus { outline: none; border-color: var(--accent); }
  .toolbar-sep { width: 1px; height: 32px; background: var(--border); margin: 0 4px; }
  .save-btn { background: var(--accent); color: #fff; border: none; border-radius: 6px; padding: 7px 18px; font-size: 13px; font-weight: 600; cursor: pointer; }
  .save-btn:hover { opacity: 0.88; }
  .save-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .del-btn { background: none; border: 1px solid var(--border); color: var(--red); border-radius: 6px; padding: 7px 14px; font-size: 13px; cursor: pointer; }
  .del-btn:hover { border-color: var(--red); background: rgba(248,113,113,0.08); }
  .status-msg { font-size: 12px; margin-left: 8px; }
  .status-msg.ok { color: var(--green); }
  .status-msg.err { color: var(--red); }

  #monaco-container { flex: 1; }

  .empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: var(--text-dim); }
  .empty-state h3 { color: var(--text); font-size: 16px; }
  .empty-state p { font-size: 13px; text-align: center; max-width: 320px; line-height: 1.6; }

  .logs-panel { flex-shrink: 0; height: 160px; border-top: 1px solid var(--border); background: #0a0c12; display: flex; flex-direction: column; overflow: hidden; }
  .logs-header { padding: 6px 14px; font-size: 10px; font-weight: 700; letter-spacing: 0.7px; text-transform: uppercase; color: var(--text-dim); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
  .logs-header span { flex: 1; }
  .logs-clear { background: none; border: none; color: var(--text-dim); font-size: 10px; cursor: pointer; padding: 0; }
  .logs-clear:hover { color: var(--text); }
  .logs-body { flex: 1; overflow-y: auto; padding: 6px 0; font-family: var(--mono); font-size: 11px; }
  .log-row { display: flex; align-items: baseline; gap: 10px; padding: 3px 14px; line-height: 1.4; }
  .log-row:hover { background: rgba(255,255,255,0.03); }
  .log-ts { color: var(--text-dim); flex-shrink: 0; }
  .log-ok { color: var(--green); flex-shrink: 0; }
  .log-err { color: var(--red); flex-shrink: 0; }
  .log-msg { color: #a9b1d6; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .log-msg.err { color: var(--red); }
</style>
</head>
<body>

<header>
  <a href="/ui" class="logo">MCP<span>Cloud</span></a>
  <div class="badge">Skill Editor</div>
  <div class="header-right">
    <a href="/ui" class="nav-link">← Tool Browser</a>
    <a href="/ui/audit" class="nav-link">Audit Log</a>
  </div>
</header>

<div class="layout">
  <nav class="sidebar">
    <div class="sidebar-header">
      <span>Skills</span>
      <button class="new-btn" onclick="newSkill()">+ New</button>
    </div>
    <div class="skill-list" id="skill-list">
      <div style="padding:12px 14px;color:var(--text-dim);font-size:12px">Loading…</div>
    </div>
  </nav>

  <div class="editor-area">
    <div class="editor-toolbar" id="toolbar" style="display:none">
      <div class="toolbar-field">
        <div class="toolbar-label">Agent Type</div>
        <input class="toolbar-input" id="inp-agent" placeholder="e.g. jira_ops" spellcheck="false">
      </div>
      <div class="toolbar-field">
        <div class="toolbar-label">Skill Name</div>
        <input class="toolbar-input" id="inp-skill" placeholder="e.g. create_ticket" spellcheck="false">
      </div>
      <div class="toolbar-sep"></div>
      <button class="save-btn" onclick="saveSkill()" id="save-btn">Save</button>
      <button class="del-btn" id="del-btn" onclick="deleteSkill()" style="display:none">Delete</button>
      <span class="status-msg" id="status-msg"></span>
    </div>
    <div id="monaco-container"></div>
    <div class="logs-panel" id="logs-panel" style="display:none">
      <div class="logs-header">
        <span>Execution Log</span>
        <button class="logs-clear" onclick="clearLogs()">clear</button>
      </div>
      <div class="logs-body" id="logs-body"></div>
    </div>
    <div class="empty-state" id="empty-state">
      <h3>Skill Editor</h3>
      <p>Write Python skills that any MCP client can call as tools. Each skill is an async function — save it and it's live instantly.</p>
      <button class="new-btn" style="padding:8px 20px;font-size:13px" onclick="newSkill()">+ New Skill</button>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js"></script>
<script>
let editor = null
let skills = []
let activeKey = null
let isNew = false

require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' } })
require(['vs/editor/editor.main'], function() {
  editor = monaco.editor.create(document.getElementById('monaco-container'), {
    language: 'python',
    theme: 'vs-dark',
    fontSize: 13,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    lineNumbers: 'on',
    padding: { top: 12 },
    automaticLayout: true,
  })
  loadSkills()
})

async function loadSkills() {
  const res = await fetch('/api/skills')
  const data = await res.json()
  skills = data.skills || []
  renderSidebar()
}

function renderSidebar() {
  const el = document.getElementById('skill-list')
  if (!skills.length) {
    el.innerHTML = '<div style="padding:12px 14px;color:var(--text-dim);font-size:12px">No skills yet. Click + New.</div>'
    return
  }
  const groups = {}
  for (const s of skills) {
    if (!groups[s.agent_type]) groups[s.agent_type] = []
    groups[s.agent_type].push(s)
  }
  let html = ''
  for (const [at, list] of Object.entries(groups)) {
    html += `<div class="skill-group-label">${at}</div>`
    for (const s of list) {
      const key = `${s.agent_type}:${s.skill_name}`
      const active = key === activeKey ? ' active' : ''
      const dot = s.loaded ? '<span class="loaded-dot" title="Loaded"></span>' : ''
      html += `<div class="skill-item${active}" id="item-${key}" onclick="openSkill('${s.agent_type}','${s.skill_name}')">${s.skill_name}${dot}</div>`
    }
  }
  el.innerHTML = html
}

async function openSkill(agentType, skillName) {
  const res = await fetch(`/api/skills/${agentType}/${skillName}`)
  const data = await res.json()

  activeKey = `${agentType}:${skillName}`
  isNew = false

  document.getElementById('inp-agent').value = agentType
  document.getElementById('inp-skill').value = skillName
  document.getElementById('inp-agent').readOnly = true
  document.getElementById('inp-skill').readOnly = true
  document.getElementById('del-btn').style.display = 'inline-block'
  document.getElementById('toolbar').style.display = 'flex'
  document.getElementById('empty-state').style.display = 'none'
  document.getElementById('status-msg').textContent = ''

  editor.setValue(data.code)
  editor.setScrollPosition({ scrollTop: 0 })
  renderSidebar()
}

async function newSkill() {
  const res = await fetch('/api/skills/template?skill_name=my_skill')
  const data = await res.json()

  activeKey = null
  isNew = true

  document.getElementById('inp-agent').value = ''
  document.getElementById('inp-skill').value = ''
  document.getElementById('inp-agent').readOnly = false
  document.getElementById('inp-skill').readOnly = false
  document.getElementById('del-btn').style.display = 'none'
  document.getElementById('toolbar').style.display = 'flex'
  document.getElementById('empty-state').style.display = 'none'
  document.getElementById('status-msg').textContent = ''

  editor.setValue(data.code)
  editor.setScrollPosition({ scrollTop: 0 })
  document.getElementById('inp-agent').focus()
  renderSidebar()
}

async function saveSkill() {
  const agentType = document.getElementById('inp-agent').value.trim()
  const skillName = document.getElementById('inp-skill').value.trim()
  const code = editor.getValue()
  const btn = document.getElementById('save-btn')
  const msg = document.getElementById('status-msg')

  if (!agentType || !skillName) {
    msg.className = 'status-msg err'
    msg.textContent = 'Agent type and skill name are required'
    return
  }

  btn.disabled = true
  btn.textContent = 'Saving…'
  msg.textContent = ''

  try {
    const res = await fetch('/api/skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_type: agentType, skill_name: skillName, code })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Save failed')

    msg.className = 'status-msg ok'
    msg.textContent = '✓ Saved and loaded'
    activeKey = `${data.agent_type}:${data.skill_name}`
    isNew = false

    document.getElementById('inp-agent').value = data.agent_type
    document.getElementById('inp-skill').value = data.skill_name
    document.getElementById('inp-agent').readOnly = true
    document.getElementById('inp-skill').readOnly = true
    document.getElementById('del-btn').style.display = 'inline-block'

    await loadSkills()
  } catch(e) {
    msg.className = 'status-msg err'
    msg.textContent = '✗ ' + e.message
  } finally {
    btn.disabled = false
    btn.textContent = 'Save'
  }
}

async function deleteSkill() {
  if (!activeKey) return
  const [at, sn] = activeKey.split(':')
  if (!confirm(`Delete ${at}:${sn}? This cannot be undone.`)) return

  const res = await fetch(`/api/skills/${at}/${sn}`, { method: 'DELETE' })
  if (!res.ok) {
    const data = await res.json()
    alert(data.detail || 'Delete failed')
    return
  }

  stopLogsPoller()
  activeKey = null
  isNew = false
  editor.setValue('')
  document.getElementById('toolbar').style.display = 'none'
  document.getElementById('logs-panel').style.display = 'none'
  document.getElementById('empty-state').style.display = 'flex'
  await loadSkills()
}

// ── Execution log panel ───────────────────────────────────────────────────────
let logsPoller = null

function startLogsPoller() {
  stopLogsPoller()
  refreshLogs()
  logsPoller = setInterval(refreshLogs, 3000)
}

function stopLogsPoller() {
  if (logsPoller) { clearInterval(logsPoller); logsPoller = null }
}

async function refreshLogs() {
  if (!activeKey) return
  const [at, sn] = activeKey.split(':')
  const res = await fetch(`/api/skills/${at}/${sn}/logs`)
  if (!res.ok) return
  const data = await res.json()
  renderLogs(data.logs || [])
}

function renderLogs(logs) {
  const body = document.getElementById('logs-body')
  if (!logs.length) {
    body.innerHTML = '<div style="padding:6px 14px;color:var(--text-dim)">No executions yet — run the tool from the Tool Browser.</div>'
    return
  }
  body.innerHTML = logs.map(l => {
    const t = new Date(l.ts * 1000)
    const ts = t.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'})
    const badge = l.success
      ? '<span class="log-ok">✓ ok</span>'
      : '<span class="log-err">✗ err</span>'
    const msg = l.error
      ? `<span class="log-msg err">${escHtml(l.error.slice(0, 200))}</span>`
      : '<span class="log-msg">success</span>'
    return `<div class="log-row"><span class="log-ts">${ts}</span>${badge}${msg}</div>`
  }).join('')
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}

function clearLogs() {
  document.getElementById('logs-body').innerHTML =
    '<div style="padding:6px 14px;color:var(--text-dim)">Cleared — new runs will appear here.</div>'
}

// Show logs panel when a skill is opened
const _origOpen = openSkill
openSkill = async function(at, sn) {
  await _origOpen(at, sn)
  document.getElementById('logs-panel').style.display = 'flex'
  document.getElementById('logs-panel').style.flexDirection = 'column'
  startLogsPoller()
}
</script>
</body>
</html>"""


@router.get("/skills", response_class=HTMLResponse, include_in_schema=False)
async def skill_editor():
    return HTMLResponse(_SKILLS_HTML)


_AUDIT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MCPCloud · Audit Log</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0f1117; --surface: #1a1d27; --surface2: #222636;
    --border: #2e3248; --accent: #6c63ff; --accent-dim: #3d3880;
    --text: #e2e4f0; --text-dim: #7c82a8;
    --green: #4ade80; --red: #f87171; --yellow: #fbbf24;
    --mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14px; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
  header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 14px 24px; display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
  .logo { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; color: var(--text); text-decoration: none; }
  .logo span { color: var(--accent); }
  .badge { background: var(--accent-dim); color: var(--accent); font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
  .header-right { margin-left: auto; display: flex; align-items: center; gap: 14px; }
  .nav-link { background: none; border: 1px solid var(--border); color: var(--text-dim); border-radius: 6px; padding: 5px 12px; font-size: 12px; font-weight: 500; cursor: pointer; text-decoration: none; transition: border-color 0.15s, color 0.15s; }
  .nav-link:hover { border-color: var(--accent); color: var(--accent); }
  .live-dot { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-dim); }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px var(--green); }

  .main { flex: 1; overflow-y: auto; padding: 20px 24px; }

  .toolbar { display: flex; gap: 10px; align-items: center; margin-bottom: 14px; }
  .toolbar input, .toolbar select {
    background: var(--surface2); border: 1px solid var(--border); color: var(--text);
    border-radius: 6px; padding: 6px 10px; font-size: 12px; font-family: var(--mono);
  }
  .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--accent); }

  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  thead th {
    text-align: left; padding: 8px 12px; color: var(--text-dim); font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5px; font-size: 10px;
    border-bottom: 1px solid var(--border); position: sticky; top: 0; background: var(--bg);
  }
  tbody td { padding: 7px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  tbody tr:hover { background: var(--surface); }
  .mono { font-family: var(--mono); color: #a9b1d6; }
  .ok { color: var(--green); }
  .err { color: var(--red); }
  .dim { color: var(--text-dim); }
  .args {
    max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    font-family: var(--mono); color: var(--text-dim);
  }
  .empty { padding: 40px; text-align: center; color: var(--text-dim); }
</style>
</head>
<body>

<header>
  <a href="/ui" class="logo">MCP<span>Cloud</span></a>
  <div class="badge">Audit Log</div>
  <div class="header-right">
    <div class="live-dot"><div class="dot"></div>live</div>
    <a href="/ui" class="nav-link">← Tool Browser</a>
    <a href="/ui/skills" class="nav-link">Skill Editor</a>
  </div>
</header>

<div class="main">
  <div class="toolbar">
    <input id="f-agent" placeholder="Filter by agent type…" spellcheck="false" oninput="refresh()">
    <input id="f-skill" placeholder="Filter by skill name…" spellcheck="false" oninput="refresh()">
    <span class="dim" id="count"></span>
  </div>
  <table>
    <thead>
      <tr>
        <th>Time</th><th>Tool</th><th>Caller</th><th>Trace ID</th>
        <th>Arguments</th><th>Duration</th><th>Status</th>
      </tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>
  <div class="empty" id="empty" style="display:none">No tool calls recorded yet — call a tool from the Tool Browser.</div>
</div>

<script>
const $ = id => document.getElementById(id)

async function refresh() {
  const agent = $('f-agent').value.trim()
  const skill = $('f-skill').value.trim()
  const params = new URLSearchParams({ limit: '200' })
  if (agent) params.set('agent_type', agent)
  if (skill) params.set('skill_name', skill)

  try {
    const res = await fetch(`/api/audit?${params}`)
    const data = await res.json()
    render(data.entries || [])
  } catch (e) {
    $('rows').innerHTML = ''
    $('empty').style.display = 'block'
    $('empty').textContent = 'Could not reach the server.'
  }
}

function render(entries) {
  $('count').textContent = `${entries.length} call${entries.length !== 1 ? 's' : ''}`
  if (!entries.length) {
    $('rows').innerHTML = ''
    $('empty').style.display = 'block'
    return
  }
  $('empty').style.display = 'none'
  $('rows').innerHTML = entries.map(e => {
    const t = new Date(e.ts * 1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'})
    const status = e.success
      ? '<span class="ok">✓ ok</span>'
      : `<span class="err" title="${escHtml(e.error || '')}">✗ error</span>`
    const args = escHtml(JSON.stringify(e.arguments ?? {}))
    return `<tr>
      <td class="mono dim">${t}</td>
      <td class="mono">${e.tool}</td>
      <td class="mono dim">${e.company_id || '-'}</td>
      <td class="mono dim">${(e.trace_id || '-').slice(0, 8)}</td>
      <td class="args" title="${args}">${args}</td>
      <td class="mono dim">${e.duration_ms?.toFixed(1) ?? '-'} ms</td>
      <td>${status}</td>
    </tr>`
  }).join('')
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}

refresh()
setInterval(refresh, 3000)
</script>
</body>
</html>"""


@router.get("/audit", response_class=HTMLResponse, include_in_schema=False)
async def audit_log_page():
    return HTMLResponse(_AUDIT_HTML)
