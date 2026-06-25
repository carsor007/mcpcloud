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
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  header .logo {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: var(--text);
  }

  header .logo span { color: var(--accent); }

  header .badge {
    background: var(--accent-dim);
    color: var(--accent);
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.3px;
  }

  header .status {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-dim);
  }

  header .dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
  }

  .layout {
    display: flex;
    height: calc(100vh - 57px);
  }

  /* Sidebar */
  .sidebar {
    width: 260px;
    flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 12px 0;
  }

  .sidebar-section {
    padding: 6px 16px 2px;
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

  .tool-item.active {
    background: var(--surface2);
    border-left-color: var(--accent);
  }

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
  }

  /* Main panel */
  .main {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .placeholder {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--text-dim);
  }

  .placeholder .icon { font-size: 40px; }
  .placeholder p { font-size: 13px; }

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
    gap: 10px;
  }

  .card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
  }

  .card-body { padding: 16px 18px; }

  /* Tool detail */
  .tool-full-name {
    font-family: var(--mono);
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
  }

  .tool-full-desc {
    color: var(--text-dim);
    font-size: 13px;
    margin-top: 4px;
  }

  /* Schema view */
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

  /* Input textarea */
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

  /* Button */
  button.run-btn {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s, background 0.15s;
    display: flex;
    align-items: center;
    gap: 7px;
  }

  button.run-btn:hover { opacity: 0.88; }
  button.run-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  /* Result */
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

  /* Agent group label in sidebar */
  .agent-group { margin-top: 8px; }

  label.input-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: block;
    margin-bottom: 6px;
  }

  .input-hint {
    font-size: 11px;
    color: var(--text-dim);
    margin-top: 6px;
  }
</style>
</head>
<body>

<header>
  <div class="logo">a2a<span>-mcp</span></div>
  <div class="badge">Tool Browser</div>
  <div class="status">
    <div class="dot" id="status-dot"></div>
    <span id="status-text">connecting…</span>
  </div>
</header>

<div class="layout">
  <nav class="sidebar" id="sidebar">
    <div class="empty-sidebar">Loading tools…</div>
  </nav>

  <main class="main" id="main">
    <div class="placeholder">
      <div class="icon">⚡</div>
      <p>Select a tool from the sidebar to get started.</p>
    </div>
  </main>
</div>

<script>
const $ = id => document.getElementById(id)

let allTools = []
let activeToolName = null

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
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
function renderSidebar(tools) {
  if (!tools.length) {
    $('sidebar').innerHTML = '<div class="empty-sidebar">No tools registered yet.<br>Add a file to skills/ to get started.</div>'
    return
  }

  // Group by agent_type (prefix before __)
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
    const prev = document.getElementById(`item-${CSS.escape(activeToolName)}`)
    if (prev) prev.classList.remove('active')
  }
  activeToolName = name
  const item = document.getElementById(`item-${CSS.escape(name)}`)
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

// ── Build a sensible default JSON from schema ─────────────────────────────────
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
