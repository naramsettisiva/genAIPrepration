# Lab 2: Build an AI Agent with Tool Use

## Learning Objectives
- Understand the **ReAct pattern** (Reason + Act + Observe loop)
- Learn how agents use **tools** (function calling) to take real actions
- See how a **tool registry** lets an agent decide what to call
- Implement **guardrails** for write actions
- Trace multi-step autonomous reasoning

## The Big Picture

A chatbot answers questions. An **agent** takes actions. The difference is tool use.

```
User request → Agent reasons → picks a tool → calls it → observes result
            → reasons again → picks next tool → ... → final answer
```

This is the ReAct pattern: the agent alternates between **reasoning** (what should I do?) and **acting** (call a tool), using each observation to inform the next step.

## How To Run

```bash
cd <repo>/labs/lab2_agent
python3 agent_demo.py
```

The demo processes "Refill my blood pressure medication" — watch the agent:
1. Verify the member
2. Find their prescriptions
3. Check refill eligibility
4. Check pharmacy inventory
5. Submit the refill (with a confirmation guardrail!)

## Learning Exercises

1. **Run it** — watch the THINK → ACT → OBSERVE loop
2. **Say 'n' at the guardrail** — see how write-action confirmation protects against unwanted actions
3. **Add a tool** — add a `send_notification` tool and have the agent call it after refill
4. **Break eligibility** — change `last_filled` date in the code so the med isn't due; see the agent stop early
5. **Add a new intent** — build a `handle_coverage_question` flow

## Interview Talking Points

> "I built an AI agent using the ReAct pattern. The agent has a registry of tools — each with a description the LLM reads to decide when to call it. For a refill request, the agent autonomously reasons through the steps: verify member, check prescriptions, confirm eligibility, check inventory, then submit. Critically, I implemented guardrails — write actions like submitting a refill require confirmation, and every action is logged in an execution trace for auditability. This is exactly the pattern Bedrock Agents and Vertex AI Agent Builder use, just with an LLM doing the reasoning instead of my simulated logic."

## Production Mapping

| Lab | AWS | GCP |
|-----|-----|-----|
| Simulated reasoner | Bedrock Agent (Claude reasons) | Vertex AI Agent (Gemini reasons) |
| Tool registry | Action Groups (OpenAPI + Lambda) | Function declarations + Cloud Functions |
| Guardrails | Bedrock Guardrails | Vertex AI safety filters |
| Execution trace | Bedrock Agent traces / CloudWatch | Vertex AI logging |
