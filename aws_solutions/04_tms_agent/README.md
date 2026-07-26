# Solution 4: TMS Automation Agent (Bedrock Agents + Action Groups)

An autonomous agent that performs multi-step operations tasks (check status, reschedule
pickups, check carrier availability) by calling tools. Uses the ReAct pattern — the agent
reasons, calls a tool, observes, and continues until the task is done.

## Architecture

```
User: "Reschedule SH-001 to July 30"
   │
   ▼
Bedrock Agent (Claude reasons: check status -> check availability -> reschedule)
   │  invokes Action Group tools
   ▼
Lambda (agent_action_lambda.py)  ──► TMS API / DynamoDB
   │  returns tool results
   ▼
Agent synthesizes final answer to the user
```

## AWS Services
- **Bedrock Agents** — orchestration + reasoning (Claude)
- **Action Groups** — tools defined by `openapi.yaml`, backed by the Lambda
- **Lambda** — executes tool calls (`agent_action_lambda.py`)
- **DynamoDB** (or your TMS API) — the system of record

## Files
- `agent_action_lambda.py` — the Action Group Lambda (has `lambda_handler`)
- `openapi.yaml` — tool schema the agent reads to decide what to call

## Deploy

### Step 1 — Deploy the Action Group Lambda
```bash
cd aws_solutions/04_tms_agent
# Zip and deploy (or use SAM). Simplest:
zip function.zip agent_action_lambda.py
aws lambda create-function \
  --function-name tms-agent-actions \
  --runtime python3.12 \
  --handler agent_action_lambda.lambda_handler \
  --zip-file fileb://function.zip \
  --role <YOUR_LAMBDA_EXECUTION_ROLE_ARN>
```

### Step 2 — Create the Bedrock Agent
1. Bedrock console → **Agents** → **Create agent**
2. Foundation model: **Claude 3 Sonnet**
3. Instructions: *"You are a logistics operations agent. Help users check shipment
   status, reschedule pickups, and check carrier availability. Confirm before write
   actions like rescheduling."*
4. **Add Action Group:**
   - Action group type: **Define with API schemas**
   - Lambda: `tms-agent-actions`
   - Schema: upload `openapi.yaml`
5. Grant Bedrock permission to invoke the Lambda:
```bash
aws lambda add-permission \
  --function-name tms-agent-actions \
  --statement-id bedrock-agent \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com
```
6. **Prepare** the agent, then **Test** in the console.

### Step 3 — Test the agent
In the agent test panel, type:
> "What's the status of SH-001, and reschedule its pickup to 2026-07-30"

Watch the agent reason, call `check_shipment_status`, then `reschedule_pickup`.

### Local test of the Lambda logic (no AWS)
```bash
python3 agent_action_lambda.py
```

## Guardrails (production)
- Gate **write actions** (reschedule) behind agent confirmation prompts
- Use **Bedrock Guardrails** for PII/topic filtering
- Log every tool invocation (CloudWatch) for audit
- Least-privilege IAM on the Lambda (only the TMS/DynamoDB access it needs)

## Interview Talking Point
> "I built an autonomous operations agent with Bedrock Agents. The agent reasons with the
> ReAct pattern and calls Action Group tools — Lambda functions defined by an OpenAPI
> schema. For 'reschedule SH-001 to Thursday' it autonomously checks status, verifies
> carrier availability, then reschedules — confirming before the write. Every tool call is
> logged for audit, and write actions are gated behind confirmation."
