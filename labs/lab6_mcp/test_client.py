#!/usr/bin/env python3
"""
Lab 6: MCP Test Client
======================
Drives the MCP server exactly like Claude Desktop / Amazon Q would:
launches it as a subprocess and speaks JSON-RPC 2.0 over stdio.

This shows the full MCP conversation:
  1. initialize   (handshake)
  2. tools/list   (discover what the server offers)
  3. tools/call   (invoke tools)

Run: python3 test_client.py
"""

import json
import subprocess
import sys


def send(proc, request):
    """Send a JSON-RPC request and read the response."""
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    if request.get("id") is None:
        return None
    line = proc.stdout.readline()
    return json.loads(line)


def main():
    print("=" * 68)
    print("MCP CLIENT: launching the 'bi-insights' server as a subprocess")
    print("(this is exactly how Claude Desktop / Amazon Q connect to it)")
    print("=" * 68)

    proc = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )

    try:
        # 1. INITIALIZE
        print("\n[1] -> initialize")
        resp = send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {"protocolVersion": "2024-11-05"}})
        print(f"    <- server: {resp['result']['serverInfo']}")

        # 2. TOOLS/LIST — discover capabilities
        print("\n[2] -> tools/list")
        resp = send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        for t in resp["result"]["tools"]:
            print(f"    <- tool: {t['name']:18} — {t['description']}")

        # 3. TOOLS/CALL — the AI assistant calls tools to answer questions
        print("\n[3] Simulating AI answering user questions via tool calls:")

        print('\n    User asks: "What is our average delivery time this month?"')
        resp = send(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                           "params": {"name": "query_metric",
                                      "arguments": {"metric": "avg_delivery_time",
                                                    "period": "this_month"}}})
        print(f"    -> tools/call query_metric")
        print(f"    <- {resp['result']['content'][0]['text']}")

        print('\n    User asks: "How does cost per shipment compare to last month?"')
        resp = send(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                           "params": {"name": "compare_periods",
                                      "arguments": {"metric": "cost_per_shipment"}}})
        print(f"    -> tools/call compare_periods")
        print(f"    <- {resp['result']['content'][0]['text']}")

        print('\n    User asks: "What metrics can I ask about?"')
        resp = send(proc, {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                           "params": {"name": "list_metrics", "arguments": {}}})
        print(f"    -> tools/call list_metrics")
        print(f"    <- {resp['result']['content'][0]['text']}")

        print("\n" + "=" * 68)
        print("SUCCESS — you launched an MCP server and a client talked to it!")
        print("Any MCP-compatible AI (Claude Desktop, Amazon Q) can now use it.")
        print("=" * 68)

    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
