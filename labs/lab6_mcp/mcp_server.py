#!/usr/bin/env python3
"""
Lab 6: MCP Server from Scratch
==============================
MCP (Model Context Protocol) is the open standard (from Anthropic) that lets
AI assistants — Claude Desktop, Amazon Q, IDEs — connect to YOUR tools and
data through a uniform interface. Instead of custom integrations per app,
you build ONE MCP server and any MCP-compatible client can use it.

This is a REAL, working MCP server. It speaks the actual protocol:
JSON-RPC 2.0 over stdio. It implements the three core methods:
  - initialize      (handshake)
  - tools/list      (advertise what tools this server offers)
  - tools/call      (execute a tool)

Use case (BI insights): expose business metrics so an AI assistant can
answer "what's our average delivery time?" by calling this server's tools.

--- PRODUCTION NOTE ---
In production (Python 3.10+) you'd use the official SDK, which handles the
protocol plumbing for you:

    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("bi-insights")

    @mcp.tool()
    def query_metric(metric: str, period: str) -> str:
        '''Query a business metric for a time period.'''
        return run_query(metric, period)

    if __name__ == "__main__":
        mcp.run()   # handles stdio + JSON-RPC automatically

This file implements that plumbing by hand so you SEE what MCP actually does.

Run standalone:  python3 mcp_server.py   (then type JSON-RPC requests)
Run with client: python3 test_client.py  (drives this server automatically)
"""

import sys
import json


# ---------------------------------------------------------------------------
# "Backend" — simulated business data the MCP server exposes
# ---------------------------------------------------------------------------
METRICS_DB = {
    "avg_delivery_time": {
        "this_month": {"value": 27.8, "unit": "hours", "shipments": 5481},
        "last_month": {"value": 31.2, "unit": "hours", "shipments": 5102},
    },
    "cost_per_shipment": {
        "this_month": {"value": 55, "unit": "USD"},
        "last_month": {"value": 58, "unit": "USD"},
    },
    "on_time_rate": {
        "this_month": {"value": 94.2, "unit": "percent"},
        "last_month": {"value": 91.8, "unit": "percent"},
    },
}


# ---------------------------------------------------------------------------
# TOOL IMPLEMENTATIONS — what the AI assistant can actually call
# ---------------------------------------------------------------------------
def tool_query_metric(metric: str, period: str = "this_month") -> str:
    m = METRICS_DB.get(metric)
    if not m:
        return f"Unknown metric '{metric}'. Available: {', '.join(METRICS_DB)}"
    data = m.get(period)
    if not data:
        return f"No data for period '{period}'."
    return f"{metric} ({period}): {data['value']} {data['unit']}"


def tool_compare_periods(metric: str) -> str:
    m = METRICS_DB.get(metric)
    if not m:
        return f"Unknown metric '{metric}'."
    now = m["this_month"]["value"]
    prev = m["last_month"]["value"]
    delta = now - prev
    pct = (delta / prev) * 100
    direction = "up" if delta > 0 else "down"
    return (f"{metric}: {now} this month vs {prev} last month "
            f"({direction} {abs(pct):.1f}%)")


def tool_list_metrics() -> str:
    return "Available metrics: " + ", ".join(METRICS_DB.keys())


# ---------------------------------------------------------------------------
# TOOL REGISTRY — advertised to clients via tools/list
# The 'inputSchema' is JSON Schema; the AI reads 'description' to decide usage.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "query_metric",
        "description": "Get the value of a business metric for a time period.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string",
                           "description": "Metric name, e.g. avg_delivery_time"},
                "period": {"type": "string",
                           "description": "this_month or last_month"},
            },
            "required": ["metric"],
        },
        "_fn": tool_query_metric,
    },
    {
        "name": "compare_periods",
        "description": "Compare a metric between this month and last month.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "Metric name"},
            },
            "required": ["metric"],
        },
        "_fn": tool_compare_periods,
    },
    {
        "name": "list_metrics",
        "description": "List all available business metrics.",
        "inputSchema": {"type": "object", "properties": {}},
        "_fn": tool_list_metrics,
    },
]


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 PROTOCOL HANDLER (this is what MCP speaks under the hood)
# ---------------------------------------------------------------------------
def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params", {})

    # 1. INITIALIZE — the handshake every MCP session starts with
    if method == "initialize":
        return _result(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "bi-insights", "version": "1.0.0"},
        })

    # 2. TOOLS/LIST — advertise available tools (AI reads these to decide)
    if method == "tools/list":
        public_tools = [{k: v for k, v in t.items() if not k.startswith("_")}
                        for t in TOOLS]
        return _result(req_id, {"tools": public_tools})

    # 3. TOOLS/CALL — execute a named tool with arguments
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        tool = next((t for t in TOOLS if t["name"] == name), None)
        if not tool:
            return _error(req_id, -32602, f"Unknown tool: {name}")
        try:
            result_text = tool["_fn"](**args)
            return _result(req_id, {
                "content": [{"type": "text", "text": result_text}]
            })
        except Exception as e:
            return _error(req_id, -32603, f"Tool error: {e}")

    return _error(req_id, -32601, f"Method not found: {method}")


def _result(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


# ---------------------------------------------------------------------------
# STDIO TRANSPORT — read JSON-RPC from stdin, write responses to stdout
# This is exactly how Claude Desktop / Amazon Q launch and talk to MCP servers.
# ---------------------------------------------------------------------------
def main():
    # Log to stderr so it doesn't corrupt the JSON-RPC on stdout
    print("[MCP server 'bi-insights' started — reading JSON-RPC from stdin]",
          file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_request(req)
        # Notifications (no id) don't get a response
        if req.get("id") is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
