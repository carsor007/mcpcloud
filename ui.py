"""Tool browser UI — served at /ui."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>a2a-mcp · Tool Browser</title>
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
  <div class="logo" onclick="showGuide()">a2a<span>-mcp</span></div>
  <div class="badge">Tool Browser</div>
  <div class="header-right">
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
const SKILL_TEMPLATE = `# skills/my_tools.py
from registry import SkillResult, get_registry

async def my_skill(input: dict, context: dict) -> SkillResult:
    \'\'\'One-line description shown in this UI.\'\'\'
    value = input.get("text", "")
    return SkillResult(success=True, output={"result": value.upper()})

def register_all():
    get_registry().register(
        "my_tools",     # agent type  →  groups skills in the sidebar
        "my_skill",     # skill name  →  shown under the group
        my_skill,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "Input text"}
            }
        }
    )`

const CLAUDE_CONFIG = () => `// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "my_tools": {
      "url": "${origin}/mcp/my_tools",
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
      <div class="card-header"><div class="card-title">What is a2a-mcp?</div></div>
      <div class="card-body">
        <p class="guide-intro">
          <strong>a2a-mcp</strong> is a self-hosted MCP (Model Context Protocol) gateway.
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
                For example: <code>GET ${origin}/mcp/text_analysis/config</code>
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
                Scope to one agent type: <code>${origin}/mcp/text_analysis</code><br>
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
