# Lab 6: Building & Launching an MCP Server

## Learning Objectives
- Understand what **MCP (Model Context Protocol)** is and why it matters
- See the **MCP protocol** in action (JSON-RPC over stdio: initialize, tools/list, tools/call)
- Build and **launch a working MCP server** from scratch
- Learn how to **connect** it to AI assistants (Claude Desktop, Amazon Q)
- Know the **production SDK** approach

## What Is MCP?

MCP is an open standard (from Anthropic, now widely adopted) that lets AI assistants
connect to YOUR tools and data through ONE uniform interface. Think of it as
"USB-C for AI" — build one MCP server, and any MCP-compatible client can use it.

**Before MCP:** every AI app needed custom integrations to your systems (N×M problem).
**With MCP:** build one server, works with all MCP clients (Claude Desktop, Amazon Q, IDEs, etc.).

```
┌─────────────┐         MCP Protocol          ┌──────────────┐
│  AI Client  │ <---- (JSON-RPC / stdio) ----> │  MCP Server  │
│ (Claude,    │                                │  (YOUR tools │
│  Amazon Q)  │   initialize / tools/list /    │   & data)    │
│             │        tools/call              │              │
└─────────────┘                                └──────────────┘
```

## The Three Core Protocol Methods

| Method | Purpose |
|--------|---------|
| `initialize` | Handshake — client & server agree on protocol version & capabilities |
| `tools/list` | Server advertises its tools (name, description, input schema) |
| `tools/call` | Client invokes a tool by name with arguments; server returns result |

## What's In This Lab

- `mcp_server.py` — **RUNNABLE** — a real MCP server (BI insights use case) implementing the full protocol by hand
- `test_client.py` — **RUNNABLE** — a client that launches the server and drives the full conversation
- Use case: expose business metrics so an AI can answer "what's our avg delivery time?"

## How To Run

```bash
cd <repo>/labs/lab6_mcp

# Run the client — it launches the server and shows the full MCP conversation
python3 test_client.py

# Or run the server standalone and type JSON-RPC yourself:
python3 mcp_server.py
# then paste:  {"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

## How To Launch It With a Real AI Assistant

**Amazon Q Developer / Claude Desktop** launch MCP servers via a config file. Example
(`claude_desktop_config.json` or Q's MCP config):

```json
{
  "mcpServers": {
    "bi-insights": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

The AI client launches your server as a subprocess, calls `initialize`, discovers tools
via `tools/list`, and calls them with `tools/call` — exactly what `test_client.py` demonstrates.

## Production Version (Python 3.10+, official SDK)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bi-insights")

@mcp.tool()
def query_metric(metric: str, period: str = "this_month") -> str:
    """Get the value of a business metric for a time period."""
    return run_query(metric, period)

if __name__ == "__main__":
    mcp.run()   # SDK handles stdio + JSON-RPC plumbing
```

The SDK hides the protocol plumbing — but this lab shows you what it does underneath.

## Learning Exercises

1. **Run test_client.py** — watch the initialize → list → call flow
2. **Add a tool** — add a `forecast_metric` tool to `mcp_server.py`, expose it in `TOOLS`
3. **Run the server standalone** — paste raw JSON-RPC and see responses
4. **Trace the protocol** — add logging to see every request/response
5. **Add a resource** — MCP also supports "resources" (read-only data) and "prompts"

## Interview Talking Points

> "I built and launched an MCP server. MCP is the open standard that lets AI assistants
> connect to your tools and data uniformly — build one server, and any MCP client like
> Claude Desktop or Amazon Q can use it. Under the hood it's JSON-RPC over stdio with three
> core methods: initialize for the handshake, tools/list to advertise capabilities, and
> tools/call to execute. I exposed business metrics as tools so an AI could answer BI
> questions by calling my server rather than me building a custom integration per app. In
> production you'd use the FastMCP SDK, but I implemented the protocol by hand so I
> understand exactly what's happening — and that matters for debugging, security, and auth."

## Security Considerations (mention these — shows maturity)

- **Auth:** MCP servers often need auth (API keys, OAuth) before exposing sensitive tools
- **Least privilege:** only expose the tools/data the AI actually needs
- **Input validation:** validate tool arguments (they come from an LLM — treat as untrusted)
- **Read vs write:** gate write actions behind confirmation (see Lab 2 guardrails)
- **Audit logging:** log every tool call for traceability (critical in regulated industries)
