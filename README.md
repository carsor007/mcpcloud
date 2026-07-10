# MCPCloud

Self-hosted MCP (Model Context Protocol) gateway. Write any Python function, register it as a skill, and it instantly becomes a tool that Claude Desktop, Claude API, Cursor, or any MCP-compatible client can call.

[![Deploy to Cloud](https://img.shields.io/badge/Deploy%20to%20Cloud-AWS%20Marketplace-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/marketplace/pp/prodview-6ujgmfv3k42hu)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)

**Website:** [mcpcloud.dev](https://mcpcloud.dev) · **Demo:** [demo.mcpcloud.dev](https://demo.mcpcloud.dev) · **GitHub:** [carsor007/mcpcloud](https://github.com/carsor007/mcpcloud)

---

## How it works

```
Claude Desktop / Claude API / any MCP client
            ↓  MCP tool call
        MCPCloud  (this repo)
            ↓  your code runs
    Jira · Slack · Salesforce · anything
```

Every Python function registered as a skill becomes an MCP tool. No vendor lock-in, no proprietary agent framework — just functions.

---

## Quickstart

### Deploy to Cloud

Subscribe on [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-6ujgmfv3k42hu) for a fully managed deployment on ECS Fargate — no Docker, no ECR setup, no servers to manage. Includes a 7-day free trial.

### Run locally with Docker

```bash
git clone https://github.com/carsor007/mcpcloud.git
cd mcpcloud
cp .env.example .env
docker compose up
```

Open **http://localhost:8000/ui** — the tool browser shows all registered skills.

---

## Connect an MCP client

MCPCloud exposes a config endpoint for every agent type. Use it to generate a ready-to-paste snippet for any MCP client.

### Claude Desktop

1. Install Claude Desktop from [claude.ai/download](https://claude.ai/download)
2. Get the config snippet for the skills you want:

```bash
curl http://localhost:8000/mcp/jira_ops/config
```

3. Open (or create) `~/Library/Application Support/Claude/claude_desktop_config.json` and add the returned snippet under `mcpServers`:

```json
{
  "mcpServers": {
    "jira_ops": {
      "url": "http://localhost:8000/mcp/jira_ops",
      "transport": "http"
    },
    "slack_ops": {
      "url": "http://localhost:8000/mcp/slack_ops",
      "transport": "http"
    }
  }
}
```

4. Restart Claude Desktop. Your skills appear as tools in every conversation.

> **Cloud deployment:** replace `http://localhost:8000` with your MCPCloud URL (e.g. `https://demo.mcpcloud.dev`).

### Cursor

Add the same JSON to `.cursor/mcp.json` in your project root, or globally at `~/.cursor/mcp.json`. The URL and transport fields are identical.

### Claude API (programmatic)

Pass the MCP server URL when initializing a client session — the endpoint follows the MCP 2025-03-26 spec over HTTP.

---

## Adding a skill

Drop a `.py` file into `skills/`. Any file with a `register_all()` function is loaded automatically on startup.

```python
# skills/my_tools.py
from registry import SkillResult, get_registry

async def my_skill(input: dict, context: dict) -> SkillResult:
    '''One-line description shown in the UI.'''
    return SkillResult(success=True, output={"result": input.get("text", "")})

def register_all():
    get_registry().register(
        "my_tools",   # agent type  — groups skills in the sidebar
        "my_skill",   # skill name  — shown under the group
        my_skill,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "Input text"}
            }
        }
    )
```

Restart the server. The skill appears in the UI and is immediately callable as an MCP tool.

---

## Included skills

Both work out of the box — real API calls run when credentials are configured, stub data is returned otherwise.

### `jira_ops`

| Skill | Description |
|---|---|
| `create_ticket` | Create a Jira issue with priority, type, and description |
| `get_ticket` | Fetch status, assignee, and priority by issue key |
| `search_tickets` | Run a JQL query and return a summary list |

Configure by setting `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` in `.env`.

### `slack_ops`

| Skill | Description |
|---|---|
| `send_message` | Post a message to a channel with optional field grid |
| `alert` | Send an urgent alert with severity badge — critical sends `@channel` |

Configure by setting `SLACK_WEBHOOK_URL` in `.env`.

---

## Audit log

Every tool call is recorded — caller, tool name, arguments, success/failure, and latency — and available at:

- **UI:** `http://localhost:8000/ui/audit` — live table, auto-refreshes every 3s, filterable by agent type/skill name
- **API:** `GET /api/audit?agent_type=jira_ops&skill_name=get_ticket&limit=100`

Entries are also emitted as structured JSON log lines, so they flow into CloudWatch Logs (or any log pipeline) for SIEM ingestion. Backed by Redis when `REDIS_URL` is set (survives restarts, shared across workers); falls back to an in-memory ring buffer otherwise.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `REDIS_URL` | No | Enables multi-worker session tracking. Set automatically in Docker Compose and CloudFormation. |
| `JIRA_URL` | No | e.g. `https://your-domain.atlassian.net` |
| `JIRA_EMAIL` | No | Atlassian account email |
| `JIRA_API_TOKEN` | No | [Create at Atlassian](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_PROJECT` | No | Default project key (default: `IT`) |
| `SLACK_WEBHOOK_URL` | No | [Create at Slack](https://api.slack.com/apps) |
| `ANTHROPIC_API_KEY` | No | Required only by skills that call Claude |
| `OPENAI_API_KEY` | No | Required only by skills that call OpenAI |

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

Free to self-host. Managed deployment available on [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-6ujgmfv3k42hu).
