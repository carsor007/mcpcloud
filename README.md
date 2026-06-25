# a2a-mcp

Self-hosted MCP (Model Context Protocol) gateway. Write any Python function, register it as a skill, and it instantly becomes a tool that Claude Desktop, Claude API, Cursor, or any MCP-compatible client can call.

[![Deploy to AWS](https://img.shields.io/badge/Deploy%20to%20AWS-ECS%20Fargate-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://console.aws.amazon.com/cloudformation/home#/stacks/create/review?templateURL=https://raw.githubusercontent.com/carsor007/a2a-mcp/main/deploy/aws/cloudformation.yaml&stackName=a2a-mcp)
[![AWS Marketplace](https://img.shields.io/badge/AWS%20Marketplace-Subscribe-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/marketplace)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)

---

## How it works

```
Claude Desktop / Claude API / any MCP client
            ↓  MCP tool call
        a2a-mcp  (this repo)
            ↓  your code runs
    Jira · Slack · Salesforce · anything
```

Every Python function registered as a skill becomes an MCP tool. No vendor lock-in, no proprietary agent framework — just functions.

---

## Quickstart

**Run locally with Docker:**

```bash
git clone https://github.com/carsor007/a2a-mcp.git
cd a2a-mcp
cp .env.example .env
docker compose up
```

Open **http://localhost:8000/ui** — the tool browser shows all registered skills.

**Connect Claude Desktop:**

```bash
curl http://localhost:8000/mcp/jira_ops/config
```

Paste the returned JSON into `~/Library/Application Support/Claude/claude_desktop_config.json` under `"mcpServers"`. Restart Claude Desktop.

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

## Deploy to AWS

The **Deploy to AWS** button above launches the CloudFormation stack in your account. It provisions:

- **ECS Fargate** — 2 tasks, no EC2 to manage
- **ElastiCache Redis** — session tracking across workers (~$15/month for t4g.micro)
- **Application Load Balancer** — with optional HTTPS via ACM
- **Secrets Manager** — stores Jira, Slack, and API credentials securely

You will need: a VPC with at least 2 public subnets, and an ECR image (see below).

**Push the image to ECR first:**

```bash
cd deploy/aws
make ecr-create
make push
```

Then click **Deploy to AWS** or run:

```bash
make deploy \
  VPC_ID=vpc-xxxxxxxxxxxxxxxxx \
  PUBLIC_SUBNETS=subnet-aaa,subnet-bbb \
  PRIVATE_SUBNETS=subnet-ccc,subnet-ddd
```

After deployment, retrieve your URLs:

```bash
make outputs
```

---

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
