#!/usr/bin/env python3
"""
Lab 2: AI Agent with Tool Use (ReAct Pattern)
==============================================
A working agent that REASONS about what to do and ACTS by calling tools.

This simulates the ReAct loop (Reason + Act) that powers Bedrock Agents,
Vertex AI Agents, and frameworks like LangGraph. We use a rule-based
"reasoner" here so it runs without an API key — but the ARCHITECTURE
(tools, registry, reasoning loop, guardrails) is exactly what you'd
describe in an interview.

Run: python3 agent_demo.py
"""

import json
import re
from datetime import datetime, timedelta

# ===========================================================================
# TOOLS — In a real agent, each of these is an API/Lambda the agent can call.
# Each tool has: a name, a description (the LLM reads this to decide when to
# use it), and an implementation.
# ===========================================================================

# Simulated backend data
MEMBERS = {
    "MBR-12345": {"name": "Jane Doe", "plan": "HealthConnect (sample) Gold"},
}
PRESCRIPTIONS = {
    "MBR-12345": [
        {"rx_id": "RX-567", "drug": "Lisinopril 10mg", "last_filled": "2026-07-01",
         "days_supply": 30, "refills_left": 3},
    ],
}
PHARMACY_INVENTORY = {
    "Lisinopril 10mg": {"in_stock": True, "ready_in_hours": 2},
}


def get_member_profile(member_id: str) -> dict:
    """Look up a member's profile by member ID."""
    member = MEMBERS.get(member_id)
    if not member:
        return {"error": f"No member found with ID {member_id}"}
    return {"member_id": member_id, **member}


def check_prescriptions(member_id: str) -> dict:
    """Get the list of prescriptions for a member."""
    rxs = PRESCRIPTIONS.get(member_id, [])
    return {"member_id": member_id, "prescriptions": rxs}


def check_refill_eligibility(rx_id: str, member_id: str) -> dict:
    """Check if a prescription is eligible for refill (25% or less remaining)."""
    for rx in PRESCRIPTIONS.get(member_id, []):
        if rx["rx_id"] == rx_id:
            last_filled = datetime.strptime(rx["last_filled"], "%Y-%m-%d")
            days_elapsed = (datetime.now() - last_filled).days
            pct_remaining = max(0, (rx["days_supply"] - days_elapsed) / rx["days_supply"])
            eligible = pct_remaining <= 0.25 and rx["refills_left"] > 0
            return {"rx_id": rx_id, "eligible": eligible,
                    "pct_remaining": round(pct_remaining * 100),
                    "refills_left": rx["refills_left"]}
    return {"error": f"No prescription {rx_id} found"}


def check_pharmacy_inventory(drug: str) -> dict:
    """Check if a drug is in stock at the pharmacy."""
    inv = PHARMACY_INVENTORY.get(drug)
    if not inv:
        return {"drug": drug, "in_stock": False}
    return {"drug": drug, **inv}


def submit_refill(rx_id: str, member_id: str) -> dict:
    """Submit a prescription refill. THIS IS A WRITE ACTION — needs confirmation."""
    return {"rx_id": rx_id, "status": "submitted",
            "ready_by": (datetime.now() + timedelta(hours=2)).strftime("%I:%M %p")}


# Tool registry — the agent reads these descriptions to decide what to call
TOOLS = {
    "get_member_profile": {
        "fn": get_member_profile,
        "description": "Get a member's profile. Args: member_id",
        "write": False,
    },
    "check_prescriptions": {
        "fn": check_prescriptions,
        "description": "List a member's prescriptions. Args: member_id",
        "write": False,
    },
    "check_refill_eligibility": {
        "fn": check_refill_eligibility,
        "description": "Check if an Rx can be refilled. Args: rx_id, member_id",
        "write": False,
    },
    "check_pharmacy_inventory": {
        "fn": check_pharmacy_inventory,
        "description": "Check drug stock. Args: drug",
        "write": False,
    },
    "submit_refill": {
        "fn": submit_refill,
        "description": "Submit a refill (WRITE). Args: rx_id, member_id",
        "write": True,
    },
}


# ===========================================================================
# THE AGENT — ReAct loop: THINK -> ACT -> OBSERVE -> repeat
# In production, an LLM generates the THINK and decides the ACT. Here we
# simulate that reasoning to demonstrate the pattern deterministically.
# ===========================================================================

class Agent:
    def __init__(self, tools, require_confirmation=True):
        self.tools = tools
        self.require_confirmation = require_confirmation
        self.trace = []

    def call_tool(self, name, **kwargs):
        tool = self.tools[name]
        # GUARDRAIL: write actions require confirmation
        if tool["write"] and self.require_confirmation:
            print(f"\n  ⚠️  GUARDRAIL: '{name}' is a WRITE action.")
            confirm = input(f"     Confirm {name}({kwargs})? [y/n]: ").strip().lower()
            if confirm != "y":
                return {"status": "cancelled_by_user"}
        result = tool["fn"](**kwargs)
        self.trace.append({"action": name, "args": kwargs, "result": result})
        return result

    def think(self, thought):
        print(f"\n  🧠 THOUGHT: {thought}")

    def act(self, name, **kwargs):
        print(f"  🔧 ACTION: {name}({kwargs})")
        result = self.call_tool(name, **kwargs)
        print(f"  👀 OBSERVATION: {json.dumps(result)}")
        return result

    def handle_refill_request(self, member_id):
        """
        Demonstrates multi-step agentic reasoning for: 'refill my medication'
        This is the ReAct loop a real LLM agent would execute autonomously.
        """
        print("\n" + "=" * 70)
        print("AGENT PROCESSING: 'Refill my blood pressure medication'")
        print("=" * 70)

        # Step 1: Reason about verifying the member
        self.think("I need to verify the member before doing anything.")
        profile = self.act("get_member_profile", member_id=member_id)
        if "error" in profile:
            return "I couldn't verify your account. Please check your member ID."

        # Step 2: Find their prescriptions
        self.think(f"Member {profile['name']} verified. Now find their prescriptions.")
        rxs = self.act("check_prescriptions", member_id=member_id)
        if not rxs["prescriptions"]:
            return "I don't see any prescriptions on file."

        rx = rxs["prescriptions"][0]  # blood pressure med
        self.think(f"Found {rx['drug']}. Check if it's eligible for refill.")

        # Step 3: Check eligibility
        elig = self.act("check_refill_eligibility",
                        rx_id=rx["rx_id"], member_id=member_id)
        if not elig["eligible"]:
            return (f"Your {rx['drug']} isn't due for refill yet "
                    f"({elig['pct_remaining']}% remaining).")

        # Step 4: Check inventory
        self.think("Eligible. Check if the pharmacy has it in stock.")
        inv = self.act("check_pharmacy_inventory", drug=rx["drug"])
        if not inv["in_stock"]:
            return f"{rx['drug']} is currently out of stock. I can notify you when available."

        # Step 5: Submit the refill (write action -> guardrail kicks in)
        self.think("All checks pass. Submit the refill.")
        result = self.act("submit_refill", rx_id=rx["rx_id"], member_id=member_id)
        if result.get("status") == "cancelled_by_user":
            return "No problem, I've cancelled the refill request."

        return (f"Done! Your {rx['drug']} refill is submitted and will be "
                f"ready by {result['ready_by']} today. Anything else?")


def main():
    print("\n" + "#" * 70)
    print("# LAB 2: AI AGENT WITH TOOL USE (ReAct Pattern)")
    print("#" * 70)
    print("\nThis agent will process a refill request, reasoning step-by-step")
    print("and calling tools. Watch the THINK -> ACT -> OBSERVE loop.\n")

    agent = Agent(TOOLS, require_confirmation=True)
    final = agent.handle_refill_request("MBR-12345")

    print("\n" + "=" * 70)
    print("FINAL AGENT RESPONSE:")
    print("=" * 70)
    print(f"  💬 {final}")

    print("\n" + "=" * 70)
    print("FULL EXECUTION TRACE (what tools were called):")
    print("=" * 70)
    for i, step in enumerate(agent.trace, 1):
        print(f"  {i}. {step['action']}({step['args']})")

    print("\nYou just ran an agent with the ReAct pattern + tool guardrails!\n")


if __name__ == "__main__":
    main()
