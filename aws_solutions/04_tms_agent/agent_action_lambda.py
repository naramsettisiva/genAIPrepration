#!/usr/bin/env python3
"""
Solution 4: TMS Automation Agent (AWS Bedrock Agents + Action Groups)
====================================================================
A Bedrock Agent that autonomously performs multi-step operations tasks by
calling tools (Action Groups). This file is the Lambda that BACKS the Action
Group — Bedrock invokes it when the agent decides to use a tool.

The agent itself is created in the Bedrock console / via API (see README) and
points to this Lambda + the openapi.yaml schema.

Flow: user request -> Bedrock Agent (Claude reasons) -> invokes this Lambda tool
      -> Lambda calls TMS/DynamoDB -> returns result -> agent continues/answers

Prereqs: Bedrock Agents, this Lambda, DynamoDB table (or your TMS API).
"""

import json
import os

# In production these call your real TMS / DynamoDB. Simulated here for portability.
SHIPMENTS = {
    "SH-001": {"status": "scheduled", "pickup_date": "2026-07-27", "origin": "Nashville"},
    "SH-002": {"status": "in_transit", "eta": "2026-07-28", "origin": "Memphis"},
}


def check_shipment_status(shipment_id):
    s = SHIPMENTS.get(shipment_id)
    if not s:
        return {"error": f"Shipment {shipment_id} not found"}
    return {"shipment_id": shipment_id, **s}


def reschedule_pickup(shipment_id, new_date):
    if shipment_id not in SHIPMENTS:
        return {"error": f"Shipment {shipment_id} not found"}
    SHIPMENTS[shipment_id]["pickup_date"] = new_date
    return {"shipment_id": shipment_id, "status": "rescheduled", "new_date": new_date}


def get_carrier_availability(origin, date):
    # Simulated availability lookup
    return {"origin": origin, "date": date, "available": True, "slots": ["AM", "PM"]}


# Map action-group API paths to functions
DISPATCH = {
    "/check_shipment_status": lambda p: check_shipment_status(p["shipment_id"]),
    "/reschedule_pickup": lambda p: reschedule_pickup(p["shipment_id"], p["new_date"]),
    "/get_carrier_availability": lambda p: get_carrier_availability(p["origin"], p["date"]),
}


def lambda_handler(event, context):
    """
    Bedrock Agent Action Group handler. Bedrock sends the apiPath + parameters;
    we execute and return in the format Bedrock expects.
    """
    api_path = event.get("apiPath", "")
    # Bedrock passes parameters as a list; flatten to a dict
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    # Also support requestBody-style params
    try:
        props = event["requestBody"]["content"]["application/json"]["properties"]
        params.update({p["name"]: p["value"] for p in props})
    except (KeyError, TypeError):
        pass

    fn = DISPATCH.get(api_path)
    result = fn(params) if fn else {"error": f"Unknown path {api_path}"}

    # Response format required by Bedrock Agents
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "tms-actions"),
            "apiPath": api_path,
            "httpMethod": event.get("httpMethod", "POST"),
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {"body": json.dumps(result)}
            },
        },
    }


# Local test harness (simulates what Bedrock would send)
if __name__ == "__main__":
    print("=" * 60)
    print("Solution 4: TMS Agent Action Group Lambda (local test)")
    print("=" * 60)
    tests = [
        {"apiPath": "/check_shipment_status",
         "parameters": [{"name": "shipment_id", "value": "SH-001"}]},
        {"apiPath": "/reschedule_pickup",
         "parameters": [{"name": "shipment_id", "value": "SH-001"},
                        {"name": "new_date", "value": "2026-07-30"}]},
        {"apiPath": "/get_carrier_availability",
         "parameters": [{"name": "origin", "value": "Nashville"},
                        {"name": "date", "value": "2026-07-30"}]},
    ]
    for t in tests:
        out = lambda_handler(t, None)
        body = out["response"]["responseBody"]["application/json"]["body"]
        print(f"\n{t['apiPath']} -> {body}")
