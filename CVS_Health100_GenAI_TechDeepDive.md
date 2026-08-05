# GenAI Technical Deep Dive — AWS Solutions for Your 6 Proof Points

## Purpose
This document gives you the technical depth to walk through each solution end-to-end in an HM interview. You launched these initiatives — now here's the "how it works under the hood" so you can speak fluently about architecture, trade-offs, and design decisions.

> 🚀 **Deployable code for every solution below** lives in [`aws_solutions/`](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions) — working Python, SAM/CloudFormation templates, and step-by-step AWS deploy guides. Each use case links to its implementation.

---

## 1. AI-Powered Shipper Support (→ Amazon Connect + Bedrock Agents)

> 📺 **Watch first:** [What is RAG?](https://www.youtube.com/watch?v=T-D1OfcDW1M) (IBM, 7 min) · [Integrating Foundation Models with Amazon Bedrock](https://www.youtube.com/watch?v=ab1mbj0acDo) (AWS) · [Learn RAG From Scratch](https://www.youtube.com/watch?v=sVcwVQRHIc8) (freeCodeCamp, full course)

> 💻 **Deploy it:** [aws_solutions/01_ai_customer_support](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/01_ai_customer_support)

### What You Launched
An AI system that automatically handles shipper inquiries — answering questions, resolving issues, and escalating only when necessary.

### Architecture Diagram (Mental Model)

```
Shipper contacts support (phone/chat/email)
         │
         ▼
┌─────────────────────────────────────┐
│     Amazon Connect (Omnichannel)     │
│  • Receives call/chat/email          │
│  • Identifies shipper (phone/email)  │
│  • Passes to AI Agent                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Amazon Bedrock Agent             │
│  • Understands shipper's intent      │
│  • Retrieves context (RAG)           │
│  • Takes actions via tool-use        │
│  • Generates natural language reply  │
└──────────┬────────────┬─────────────┘
           │            │
           ▼            ▼
┌──────────────┐  ┌──────────────────┐
│ Knowledge Base│  │ Action Groups     │
│ (RAG)        │  │ (API integrations)│
│ • FAQs       │  │ • Check shipment  │
│ • Policies   │  │ • Update ETA      │
│ • SOPs       │  │ • Create ticket   │
│ • Past cases │  │ • Escalate        │
└──────────────┘  └──────────────────┘
                          │
                          ▼
              ┌────────────────────┐
              │ Backend Systems     │
              │ • TMS (shipments)   │
              │ • CRM (customer)    │
              │ • Ticketing system   │
              └────────────────────┘
```

### How It Works Step-by-Step

1. **Shipper contacts support** via phone, chat, or email
2. **Amazon Connect** receives the contact, identifies the shipper using phone number or email match against Customer Profiles
3. **Intent detection:** Connect's conversational AI (powered by Lex + Bedrock) determines what the shipper wants:
   - "Where is my shipment?" → Track & Trace
   - "My delivery is late" → Exception handling
   - "I need to change pickup time" → Schedule modification
4. **Bedrock Agent activates:**
   - **Reasoning:** The agent's orchestration layer (ReAct pattern) decides what information it needs
   - **RAG retrieval:** Queries the Knowledge Base (backed by OpenSearch Serverless vector store) for relevant policies, SOPs, or similar past cases
   - **Tool use:** Calls Action Groups (Lambda functions) that hit your TMS API, CRM, etc.
   - **Response generation:** Synthesizes a natural language answer grounded in retrieved facts
5. **Resolution or escalation:**
   - If resolved → Agent delivers answer, generates summary, closes contact
   - If complex → Transfers to human agent with full context (transcript + summary + customer profile)

### Key AWS Services Involved

| Service | Role | Why This Choice |
|---------|------|-----------------|
| Amazon Connect | Omnichannel contact routing | Single platform for voice/chat/email, built-in AI |
| Amazon Bedrock | LLM inference (Claude/Nova) | Managed, no infrastructure to run |
| Bedrock Agents | Orchestration + tool use | Handles multi-step reasoning without custom code |
| Bedrock Knowledge Bases | RAG (vector search) | Ingests docs, chunks, embeds, retrieves automatically |
| OpenSearch Serverless | Vector store for RAG | Scales to zero, no cluster management |
| AWS Lambda | Action Groups (API calls) | Serverless functions that call your backend systems |
| Amazon S3 | Document storage for KB | Store FAQs, policies, SOPs as source documents |
| Amazon Connect Customer Profiles | Shipper identity | Unifies shipper data from CRM + contact history |

### Technical Details You Should Know

**RAG (Retrieval-Augmented Generation):**
- Documents (PDFs, HTML, Word) stored in S3
- Bedrock Knowledge Base automatically: chunks documents → generates embeddings (Titan Embeddings v2) → stores in vector DB
- At query time: user question → embed → vector similarity search → top-K chunks retrieved → passed as context to LLM → grounded answer generated
- **Why RAG vs. fine-tuning:** RAG keeps knowledge current (just update S3 docs), cheaper, no model retraining, auditable (you can see which docs were retrieved)

**Agent Orchestration (ReAct Pattern):**
- Agent receives user query + system instructions
- Agent THINKS: "I need to check shipment status for tracking #XYZ"
- Agent ACTS: Calls `check_shipment_status` tool with tracking number
- Agent OBSERVES: Gets result (delivered, in transit, delayed)
- Agent THINKS: "Shipment is delayed. I should check the reason and provide an updated ETA"
- Agent ACTS: Calls `get_delay_reason` tool
- This loop continues until the agent has enough info to respond

**Guardrails:**
- Bedrock Guardrails filter: PII, toxic content, off-topic requests
- You can define "denied topics" (e.g., "Don't discuss competitor pricing")
- Configurable thresholds for when to escalate to human

### How You Talk About It in Interview

> "We built an AI-powered support system on Amazon Connect with Bedrock Agents. The architecture uses RAG for knowledge grounding — shipper policies, SOPs, and historical case resolutions are chunked and stored in a vector database. When a shipper contacts us, the AI Agent reasons through their request, retrieves relevant context from the knowledge base, and can take actions like checking shipment status or updating delivery times through API integrations. We saw X% of inquiries resolved without human intervention, reducing average handle time by Y%."

---

## 2. Case Categorization (→ RAG + LLM Classification)

> 📺 **Watch:** [What is RAG?](https://www.youtube.com/watch?v=T-D1OfcDW1M) (IBM) · [LLMs explained briefly](https://www.youtube.com/watch?v=LPZh9BOjkQs) (3Blue1Brown, 7 min) — few-shot prompting context

> 💻 **Deploy it:** [aws_solutions/02_case_categorization](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/02_case_categorization)

### What You Launched
An AI system that automatically categorizes incoming support cases by type/intent, reducing manual triage effort.

### Architecture

```
Incoming case (email/chat/form submission)
         │
         ▼
┌─────────────────────────────────────┐
│     Ingestion Layer                  │
│  • Amazon SQS (queue)                │
│  • Lambda trigger                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Classification Pipeline          │
│                                      │
│  Step 1: Embed incoming case text    │
│     (Titan Embeddings)               │
│                                      │
│  Step 2: Retrieve similar past cases │
│     (Vector search - top 5)          │
│                                      │
│  Step 3: LLM classifies with context │
│     Prompt: "Given this case and     │
│     these similar past cases,        │
│     classify into: [categories]"     │
│                                      │
│  Step 4: Confidence check            │
│     High confidence → auto-route     │
│     Low confidence → human review    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Routing & Assignment             │
│  • Route to correct queue/team       │
│  • Set priority (P1/P2/P3)          │
│  • Assign SLA timer                  │
│  • Update CRM/ticketing system       │
└─────────────────────────────────────┘
```

### How It Works Step-by-Step

1. **Case arrives** via email, chat, or web form → lands in SQS queue
2. **Lambda triggers** classification pipeline
3. **Text preprocessing:** Extract subject, body, any attachments (using Textract for images/PDFs)
4. **Embedding:** Convert case text to vector using Amazon Titan Embeddings v2
5. **Few-shot retrieval:** Vector search against historical labeled cases → retrieve top 5 most similar cases with their categories
6. **LLM classification:** Send to Bedrock (Claude/Nova) with prompt:
   ```
   You are a case categorization system. Given this new case and 5 similar
   historical cases with their categories, classify the new case.
   
   Categories: [Shipment Delay, Billing Dispute, Pickup Scheduling,
   Rate Inquiry, Damage Claim, Account Issue, Other]
   
   New case: {case_text}
   
   Similar past cases:
   1. {similar_case_1} → Category: Shipment Delay
   2. {similar_case_2} → Category: Billing Dispute
   ...
   
   Respond with: category, confidence (high/medium/low), reasoning
   ```
7. **Confidence routing:**
   - High confidence (>90%) → auto-categorize and route
   - Medium confidence (70-90%) → auto-categorize but flag for review
   - Low confidence (<70%) → send to human triage

### Key Design Decisions

**Why RAG-based classification vs. traditional ML?**
| Approach | Pros | Cons |
|----------|------|------|
| Traditional ML (e.g., BERT classifier) | Fast inference, cheap per call | Needs labeled training data, retraining for new categories, can't explain decisions |
| RAG + LLM | No training needed, handles new categories immediately, explainable, works with few examples | Higher per-call cost, slightly slower |
| **Our choice: RAG + LLM** | Best for rapidly evolving categories, small labeled dataset, need for explanations | Cost managed by batch processing |

**Handling edge cases:**
- **New category detection:** If LLM repeatedly says "Other" with low confidence, flag for category review
- **Multi-intent cases:** Prompt instructs LLM to identify primary AND secondary intents
- **Language variations:** LLM handles natural language variations without explicit rules

### AWS Services

| Service | Role |
|---------|------|
| Amazon SQS | Queue incoming cases, decouple ingestion from processing |
| AWS Lambda | Processing logic, API calls |
| Amazon Bedrock (Titan Embeddings) | Convert text to vectors |
| Amazon OpenSearch Serverless | Vector store for historical cases |
| Amazon Bedrock (Claude/Nova) | Classification reasoning |
| Amazon DynamoDB | Store case metadata + classification results |
| Amazon EventBridge | Trigger downstream routing based on category |

### Interview Walkthrough

> "We built a RAG-based classification system. Instead of training a traditional ML model — which would need thousands of labeled examples and retraining whenever categories change — we used a few-shot retrieval approach. When a new case comes in, we embed it, find the 5 most similar historical cases from our vector store, and pass those as examples to the LLM along with the new case. The LLM classifies it and provides a confidence score. High-confidence classifications route automatically; low-confidence goes to human triage. This gave us 90%+ accuracy while being flexible enough to add new categories without retraining."

---

## 3. AI Summaries (→ Bedrock + Structured Output)

> 📺 **Watch:** [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) (Karpathy, 1 hr) — why prompt design and structured output control model behavior

> 💻 **Deploy it:** [aws_solutions/03_ai_summaries](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/03_ai_summaries)

### What You Launched
AI-generated summaries of operational data, cases, and interactions for teams to quickly understand status.

### Architecture

```
Source Data
│
├── Contact transcripts (voice/chat)
├── Case history & updates
├── Operational metrics
│
▼
┌─────────────────────────────────────┐
│     Summarization Pipeline           │
│                                      │
│  Step 1: Collect relevant data       │
│     • Pull transcript/case data      │
│     • Pull customer context          │
│     • Pull operational metrics       │
│                                      │
│  Step 2: Structured prompt           │
│     "Summarize this interaction:     │
│      - Issue: ...                    │
│      - Actions taken: ...            │
│      - Resolution: ...               │
│      - Next steps: ...               │
│      - Sentiment: ..."               │
│                                      │
│  Step 3: LLM generates summary       │
│     (Amazon Bedrock - Claude/Nova)   │
│                                      │
│  Step 4: Validate & store            │
│     • Check for PII/hallucination    │
│     • Store in case record           │
│     • Surface in dashboard           │
└─────────────────────────────────────┘
```

### Types of Summaries You Can Discuss

**1. Post-Contact Summary (after each call/chat):**
```json
{
  "issue": "Shipper reported delayed pickup for order #12345",
  "root_cause": "Driver reassigned due to capacity constraints in Nashville hub",
  "actions_taken": "Rescheduled pickup for next day, applied service credit",
  "resolution": "Resolved - new pickup confirmed for 7/26 AM window",
  "sentiment": "Negative → Neutral (improved after resolution)",
  "follow_up_required": false
}
```

**2. Case Summary (aggregates multiple interactions):**
```json
{
  "case_id": "CASE-98765",
  "created": "2024-07-20",
  "summary": "Enterprise shipper ABC Corp experiencing recurring delays at Nashville hub. 3 contacts over 5 days. Root cause: capacity planning gap for volume surge. Resolution: dedicated lane allocated starting 7/28.",
  "total_contacts": 3,
  "escalation_level": "L2 Operations",
  "business_impact": "Risk of churn - $500K annual revenue account"
}
```

**3. Operational Shift Summary (end-of-shift report):**
```json
{
  "shift": "7/24 Day Shift (6AM-6PM CT)",
  "total_contacts": 847,
  "ai_resolved": 612 (72%),
  "human_handled": 235,
  "top_issues": ["Pickup delays (34%)", "Rate inquiries (22%)", "POD requests (18%)"],
  "anomalies": "Spike in Nashville hub delay complaints (2.3x normal)",
  "recommended_actions": ["Investigate Nashville capacity", "Proactive outreach to top 5 affected shippers"]
}
```

### Key Technical Patterns

**Structured output enforcement:**
```python
# Using Bedrock with structured output
response = bedrock.invoke_model(
    modelId="anthropic.claude-v3-sonnet",
    body={
        "messages": [{"role": "user", "content": prompt}],
        "system": """You are a case summarization system. 
        Always respond in this exact JSON format:
        {"issue": "...", "actions_taken": "...", "resolution": "...", 
         "sentiment": "...", "follow_up_required": true/false}
        Do NOT include any PII (names, phone numbers, SSNs).
        Base your summary ONLY on the provided transcript."""
    }
)
```

**PII handling:**
- Amazon Comprehend detects PII entities before/after summarization
- Bedrock Guardrails configured to block PII in outputs
- For healthcare (CVS context): PHI detection + HIPAA-safe storage

### Interview Walkthrough

> "We automated post-contact summarization using Amazon Bedrock. After every interaction — voice or chat — the transcript feeds into a summarization pipeline that produces structured JSON output: issue, actions taken, resolution, sentiment, and next steps. We enforce structured output through system prompts and validate against a schema. The summaries reduce after-contact work for agents by 60-70% and give supervisors instant visibility into what's happening without reading full transcripts. We also aggregate these into shift-level and weekly operational summaries that surface trends and anomalies automatically."

---

## 4. TMS Automation via AI Agents (→ Bedrock Agents + Action Groups)

> 📺 **Watch first:** [What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI) (IBM) · [What's next for agentic workflows — Andrew Ng](https://www.youtube.com/watch?v=sal78ACtGTc) (Sequoia) · [LangChain vs LangGraph](https://www.youtube.com/watch?v=qAF1NjEVHhY) (IBM)

> 💻 **Deploy it:** [aws_solutions/04_tms_agent](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/04_tms_agent)

### What You Launched
AI Agents that autonomously interact with external Transportation Management Systems — checking status, updating records, triggering workflows.

### Architecture

```
User/System Trigger
│
├── Shipper asks "reschedule my pickup"
├── System detects SLA breach → auto-remediate
├── Operator needs bulk status update
│
▼
┌─────────────────────────────────────┐
│     Bedrock Agent (Orchestrator)     │
│                                      │
│  System Prompt:                      │
│  "You are a logistics operations     │
│   agent. You can check shipments,    │
│   update schedules, create BOLs,     │
│   and escalate exceptions."          │
│                                      │
│  Available Tools (Action Groups):    │
│  ┌─────────────────────────────┐    │
│  │ 1. check_shipment_status    │    │
│  │ 2. update_pickup_schedule   │    │
│  │ 3. get_carrier_availability │    │
│  │ 4. create_bol               │    │
│  │ 5. update_delivery_eta      │    │
│  │ 6. escalate_to_operations   │    │
│  │ 7. send_notification        │    │
│  └─────────────────────────────┘    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Action Group (Lambda Functions)  │
│                                      │
│  Each tool = Lambda function that:   │
│  • Authenticates to TMS API          │
│  • Makes API call                    │
│  • Validates response                │
│  • Returns structured result         │
│                                      │
│  Example: update_pickup_schedule     │
│  ┌────────────────────────────────┐ │
│  │ Input: shipment_id, new_date,  │ │
│  │        new_time_window         │ │
│  │ Process:                       │ │
│  │  1. GET /shipments/{id}        │ │
│  │  2. Validate new schedule      │ │
│  │  3. PUT /shipments/{id}/pickup │ │
│  │  4. Confirm update             │ │
│  │ Output: success/failure +      │ │
│  │         confirmation details   │ │
│  └────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     External Systems                 │
│  • TMS (Transportation Mgmt System) │
│  • WMS (Warehouse Mgmt System)      │
│  • Carrier portals                   │
│  • ERP (billing, invoicing)          │
└─────────────────────────────────────┘
```

### Multi-Step Agent Reasoning Example

**User request:** "Reschedule tomorrow's pickup for shipper ABC Corp to Thursday instead"

**Agent reasoning (ReAct loop):**

```
THOUGHT: I need to find ABC Corp's scheduled pickups for tomorrow.
ACTION: check_shipment_status(shipper="ABC Corp", date="2024-07-26")
OBSERVATION: Found 3 pickups scheduled: SH-001 (Nashville), SH-002 (Memphis), SH-003 (Nashville)

THOUGHT: There are 3 pickups. I should confirm which ones to reschedule. 
But the user said "tomorrow's pickup" (singular implies all). Let me check 
carrier availability for Thursday.
ACTION: get_carrier_availability(origin="Nashville", date="2024-07-28")
OBSERVATION: Carrier XYZ available, 2 slots open (AM/PM window)

ACTION: get_carrier_availability(origin="Memphis", date="2024-07-28")
OBSERVATION: Carrier DEF available, 1 slot open (PM window)

THOUGHT: Capacity available for all 3. I'll reschedule all pickups.
ACTION: update_pickup_schedule(shipment_id="SH-001", new_date="2024-07-28", window="AM")
OBSERVATION: Success - pickup rescheduled

ACTION: update_pickup_schedule(shipment_id="SH-002", new_date="2024-07-28", window="PM")
OBSERVATION: Success - pickup rescheduled

ACTION: update_pickup_schedule(shipment_id="SH-003", new_date="2024-07-28", window="AM")
OBSERVATION: Success - pickup rescheduled

THOUGHT: All 3 pickups rescheduled. I should notify the shipper.
ACTION: send_notification(shipper="ABC Corp", type="schedule_change", details=...)
OBSERVATION: Notification sent

FINAL RESPONSE: "Done! I've rescheduled all 3 of ABC Corp's pickups from 
tomorrow (7/26) to Thursday (7/28). Nashville pickups moved to the AM window, 
Memphis to PM window. ABC Corp has been notified via email."
```

### Key Design Patterns

**1. Tool Definition (OpenAPI schema):**
```yaml
# Each tool is defined as an OpenAPI spec
paths:
  /check_shipment_status:
    get:
      summary: "Check the current status of a shipment"
      parameters:
        - name: shipment_id
          type: string
          description: "The shipment tracking ID"
          required: true
      responses:
        200:
          description: "Shipment status"
          schema:
            type: object
            properties:
              status: {type: string, enum: [scheduled, in_transit, delivered, delayed]}
              eta: {type: string, format: date-time}
              current_location: {type: string}
```

**2. Guardrails for automated actions:**
- **Read-only by default:** Agent can check/read without approval
- **Write actions need confirmation:** "I'm about to reschedule 3 pickups. Proceed?"
- **Cost thresholds:** Actions above $X require human approval
- **Rollback capability:** Every action logs the previous state for undo

**3. Error handling:**
- TMS API returns error → Agent retries once → If still fails, explains to user and offers alternatives
- Partial success → Agent reports what succeeded and what didn't

### Healthcare Parallel (CVS Health100)

```
Member asks: "Refill my blood pressure medication"

THOUGHT: I need to verify the member and check their prescription.
ACTION: get_member_profile(member_id="MBR-12345")
OBSERVATION: Member verified. Has Rx #567 for Lisinopril 10mg, last filled 6/25.

THOUGHT: Rx is eligible for refill (30-day supply, 25 days elapsed). Check pharmacy availability.
ACTION: check_pharmacy_inventory(pharmacy="CVS #4521", ndc="12345-678-90")
OBSERVATION: In stock. Ready for pickup in 2 hours.

THOUGHT: All clear. Process the refill.
ACTION: submit_refill(rx_id="567", pharmacy="CVS #4521", pickup_date="today")
OBSERVATION: Refill submitted. Ready by 4:00 PM.

ACTION: send_notification(member="MBR-12345", type="refill_ready", details=...)

FINAL RESPONSE: "Your Lisinopril 10mg refill has been submitted! 
It'll be ready for pickup at CVS #4521 by 4:00 PM today. 
Need anything else?"
```

### Interview Walkthrough

> "We built AI Agents using Amazon Bedrock that can autonomously interact with our TMS and other external systems. The architecture uses the ReAct pattern — the agent reasons about what it needs to do, calls the appropriate tools (Lambda functions that wrap our TMS APIs), observes the results, and continues until the task is complete. Key design decisions: we defined clear tool schemas using OpenAPI specs, implemented guardrails so write operations require confirmation, and built rollback capability for every automated action. This pattern handles multi-step workflows that previously required operators to navigate 3-4 different systems manually."

---

## 5. MCP Servers for BI Insights (→ Natural Language to SQL/API)

> 📺 **Watch first:** [What is MCP?](https://www.youtube.com/watch?v=eur8dUO9mvE) (IBM) · [Why MCP really is a big deal](https://www.youtube.com/watch?v=FLpS7OfD5-s) (Confluent) · [Building Agents with MCP — full workshop](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) (Anthropic) · 📄 [MCP docs](https://modelcontextprotocol.io/docs/getting-started/intro)

> 💻 **Deploy it:** [aws_solutions/05_bi_insights](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/05_bi_insights)  ·  MCP server: [labs/lab6_mcp](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab6_mcp)

### What You Launched
Custom MCP (Model Context Protocol) servers that let non-technical users query business intelligence data through natural language conversations.

### Architecture

```
User: "What's our average delivery time trending this month?"
         │
         ▼
┌─────────────────────────────────────┐
│     MCP Server (Custom built)        │
│                                      │
│  Components:                         │
│  ┌────────────────────────────────┐ │
│  │ 1. Intent Parser               │ │
│  │    • Understands BI questions   │ │
│  │    • Maps to data domains       │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │ 2. Schema Context              │ │
│  │    • Table definitions          │ │
│  │    • Column descriptions        │ │
│  │    • Common query patterns      │ │
│  │    • Business metric formulas   │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │ 3. Query Generator (LLM)       │ │
│  │    • NL → SQL translation       │ │
│  │    • Validates SQL safety        │ │
│  │    • Executes query             │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │ 4. Response Formatter           │ │
│  │    • Formats results            │ │
│  │    • Generates insights         │ │
│  │    • Suggests follow-ups        │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### How Natural Language → SQL Works

**User:** "What's our average delivery time by region this month?"

**Step 1: Schema context injection**
```
System prompt includes:
- Table: shipments (id, origin_region, dest_region, pickup_time, delivery_time, status)
- Table: carriers (id, name, region, on_time_rate)
- Metric: delivery_time = delivery_time - pickup_time (in hours)
- Regions: Northeast, Southeast, Midwest, West, Southwest
- Current month filter: WHERE pickup_time >= '2024-07-01'
```

**Step 2: LLM generates SQL**
```sql
SELECT 
    dest_region,
    AVG(EXTRACT(EPOCH FROM (delivery_time - pickup_time)) / 3600) as avg_delivery_hours,
    COUNT(*) as total_shipments
FROM shipments
WHERE pickup_time >= '2024-07-01'
    AND status = 'delivered'
GROUP BY dest_region
ORDER BY avg_delivery_hours DESC;
```

**Step 3: Execute & format response**
```
Results:
| Region     | Avg Delivery (hrs) | Shipments |
|------------|-------------------|-----------|
| Northeast  | 28.3              | 1,247     |
| West       | 31.7              | 892       |
| Southeast  | 24.1              | 1,583     |
| Midwest    | 26.8              | 1,105     |
| Southwest  | 33.2              | 654       |

AI Response: "This month's average delivery times by region:
• Southeast is fastest at 24.1 hours (1,583 shipments)
• Southwest is slowest at 33.2 hours (654 shipments)
• Overall average: 27.8 hours across 5,481 deliveries

Notable: Southwest is 38% slower than Southeast despite lower volume, 
suggesting a capacity or routing issue rather than congestion.
Would you like me to drill into Southwest delays by carrier?"
```

### MCP Server Implementation Pattern

```python
# MCP Server structure (simplified)
class BIInsightsMCPServer:
    
    def __init__(self):
        self.schema_context = load_schema_descriptions()
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.redshift_client = boto3.client('redshift-data')
    
    # Tool 1: Query operational metrics
    def query_metrics(self, natural_language_question: str) -> dict:
        # Generate SQL from natural language
        sql = self._generate_sql(natural_language_question)
        
        # Safety check: only SELECT allowed, no mutations
        if not sql.strip().upper().startswith("SELECT"):
            raise SecurityError("Only read queries allowed")
        
        # Execute against Redshift/Athena
        results = self._execute_query(sql)
        
        # Generate insight narrative
        insight = self._generate_insight(natural_language_question, results)
        
        return {"data": results, "insight": insight, "sql": sql}
    
    # Tool 2: Compare time periods
    def compare_periods(self, metric: str, period1: str, period2: str) -> dict:
        ...
    
    # Tool 3: Anomaly detection
    def detect_anomalies(self, metric: str, lookback_days: int = 30) -> dict:
        ...
    
    def _generate_sql(self, question: str) -> str:
        prompt = f"""Given this database schema:
        {self.schema_context}
        
        Generate a SQL query to answer: {question}
        
        Rules:
        - Only SELECT statements
        - Always include reasonable LIMIT (max 1000)
        - Use appropriate date filters
        - Return the SQL only, no explanation"""
        
        response = self.bedrock_client.invoke_model(...)
        return response['sql']
```

### Key Design Decisions

**Security:**
- Read-only database credentials (no INSERT/UPDATE/DELETE possible)
- Query cost limits (timeout after 30 seconds, max rows)
- PII columns excluded from schema context
- All queries logged for audit

**Accuracy:**
- Schema descriptions include business context (not just column names)
- Pre-defined metric formulas prevent calculation errors
- "Did you mean...?" suggestions when query is ambiguous
- Show generated SQL so users can verify logic

**Performance:**
- Frequently asked queries cached (TTL 15 min)
- Pre-aggregated materialized views for common metrics
- Query complexity limits to prevent expensive table scans

### AWS Services

| Service | Role |
|---------|------|
| Amazon Bedrock (Claude) | NL→SQL translation + insight generation |
| Amazon Redshift Serverless | Data warehouse (OLAP queries) |
| Amazon Athena | Ad-hoc queries on S3 data lake |
| AWS Lambda | MCP server hosting |
| Amazon API Gateway | REST endpoint for MCP tools |
| Amazon CloudWatch | Query monitoring, cost tracking |

### Interview Walkthrough

> "I built custom MCP servers — essentially tool interfaces that let AI assistants query our data warehouse using natural language. The system takes a question like 'What's our delivery performance trending this month?', injects our schema context (table definitions, metric formulas, business rules), generates a safe SQL query via LLM, executes it against Redshift, and returns both the data and a narrative insight. Key design decisions: read-only credentials for safety, schema enrichment with business context for accuracy, query caching for performance, and generated SQL transparency so users can verify the logic."

---

## 6. GenAI Workshops for Product Team (→ Adoption Framework)

> 📺 **Great to screen in Workshop 1:** [LLMs explained briefly](https://www.youtube.com/watch?v=LPZh9BOjkQs) (3Blue1Brown, 7 min) · [What's next for agentic workflows](https://www.youtube.com/watch?v=sal78ACtGTc) (Andrew Ng) — sets exec-level framing

> 💻 **Program kit:** [aws_solutions/06_genai_adoption](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/06_genai_adoption)

### What You Launched
A structured workshop series that enabled Product teams to independently identify and scope AI use cases.

### Workshop Framework Architecture

```
┌─────────────────────────────────────────────────┐
│           GenAI Adoption Framework                │
│                                                   │
│  Workshop 1: "The Art of the Possible"           │
│  ├── What GenAI can/can't do (with demos)        │
│  ├── Real examples from our org                  │
│  └── Identify 10 potential use cases             │
│                                                   │
│  Workshop 2: "Use Case Evaluation"               │
│  ├── Impact × Feasibility × Risk matrix          │
│  ├── Data readiness assessment                   │
│  ├── Prioritize top 3 use cases                  │
│  └── Define success metrics upfront              │
│                                                   │
│  Workshop 3: "Responsible AI & Guardrails"       │
│  ├── What can go wrong (hallucination, bias)     │
│  ├── Human-in-the-loop design patterns           │
│  ├── Data privacy & compliance                   │
│  └── When NOT to use AI                          │
│                                                   │
│  Workshop 4: "Hands-On Prototyping"              │
│  ├── Prompt engineering basics                   │
│  ├── Build a working prototype in 2 hours        │
│  ├── Test with real data                         │
│  └── Demo to stakeholders                        │
│                                                   │
│  Outcome: Product teams can independently        │
│  identify, scope, and champion AI initiatives    │
└─────────────────────────────────────────────────┘
```

### Use Case Evaluation Matrix

| Criteria | Weight | Score (1-5) | How to Assess |
|----------|--------|-------------|---------------|
| Business Impact | 30% | ? | Revenue, cost savings, customer satisfaction |
| Data Readiness | 25% | ? | Is the data available, clean, sufficient? |
| Technical Feasibility | 20% | ? | Can current AI models handle this? |
| Risk Level | 15% | ? | What if AI is wrong? Reversible? |
| Time to Value | 10% | ? | How fast can we ship an MVP? |

**Score > 3.5:** Proceed to prototype
**Score 2.5-3.5:** Investigate further, address gaps
**Score < 2.5:** Deprioritize or redesign

### The "When NOT to Use AI" Framework (Critical for Healthcare)

```
DON'T use AI when:
├── Consequences of errors are irreversible (e.g., medication dosing)
├── Regulatory requirement for human decision (e.g., clinical diagnosis)
├── Data is insufficient or biased
├── Simple rules/logic would work (over-engineering)
└── User trust requires human accountability

DO use AI when:
├── Task is repetitive + has high variability in inputs
├── Speed matters more than 100% accuracy (with human backup)
├── Patterns exist in historical data
├── Scale makes human review impossible
└── AI augments (not replaces) human judgment
```

### Interview Walkthrough

> "I ran a structured GenAI workshop series for our Product team — four sessions that took them from 'what is GenAI' to 'here's a working prototype.' The key framework I developed is an Impact × Feasibility × Risk evaluation matrix that helps Product teams independently score and prioritize AI use cases. We also established a 'When NOT to use AI' framework — which is critical in healthcare where wrong AI outputs can have real patient safety implications. The outcome was Product teams going from waiting for engineering to propose AI features to independently bringing us prioritized, well-scoped AI opportunities."

---

## Quick Reference: End-to-End Architecture for Health100

If asked "How would you architect an AI-native health platform?":

```
┌──────────────────────────────────────────────────────────┐
│                    HEALTH100 PLATFORM                      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Consumer Experience Layer               │ │
│  │  • Mobile app  • Web portal  • Voice/Chat          │ │
│  └─────────────────────┬───────────────────────────────┘ │
│                        │                                  │
│  ┌─────────────────────▼───────────────────────────────┐ │
│  │              AI Agent Layer (Agentic)                │ │
│  │  • Health AI Agent (member-facing)                  │ │
│  │  • Provider AI Agent (clinician-facing)             │ │
│  │  • Operations AI Agent (internal)                   │ │
│  │  • Each agent has: tools, knowledge, guardrails     │ │
│  └─────────────────────┬───────────────────────────────┘ │
│                        │                                  │
│  ┌─────────────────────▼───────────────────────────────┐ │
│  │              AI Platform Layer                       │ │
│  │  • LLM inference (Gemini / Vertex AI)              │ │
│  │  • RAG (Knowledge grounding)                        │ │
│  │  • Embeddings + Vector search                       │ │
│  │  • Guardrails (PII/PHI, bias, hallucination)       │ │
│  │  • Evaluation & monitoring                          │ │
│  └─────────────────────┬───────────────────────────────┘ │
│                        │                                  │
│  ┌─────────────────────▼───────────────────────────────┐ │
│  │              Data & Integration Layer                │ │
│  │  • Unified member profile (pharmacy + insurance +   │ │
│  │    provider + claims + health records)              │ │
│  │  • Event streaming (Kafka/Pub-Sub)                 │ │
│  │  • APIs to: Pharmacy, PBM, Insurance, Providers    │ │
│  └─────────────────────┬───────────────────────────────┘ │
│                        │                                  │
│  ┌─────────────────────▼───────────────────────────────┐ │
│  │              Infrastructure (GCP/Cloud)             │ │
│  │  • GKE (Kubernetes)  • Cloud Run  • BigQuery       │ │
│  │  • Cloud SQL  • Pub/Sub  • IAM  • HIPAA controls  │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Cheat Sheet: Key Terms to Use Fluently

| Term | What It Means | When to Use |
|------|---------------|-------------|
| RAG | Retrieval-Augmented Generation — ground LLM in your data | "We used RAG to ensure accurate, grounded responses" |
| Agentic AI | AI that reasons, plans, and takes actions autonomously | "Our agents can multi-step reason through complex tasks" |
| ReAct | Reasoning + Acting loop — think, act, observe, repeat | "The agent uses a ReAct pattern to orchestrate tools" |
| Guardrails | Safety filters on AI inputs/outputs | "We implemented guardrails for PII, toxicity, and hallucination" |
| Tool use / Function calling | LLM calls external APIs | "The agent uses tool-use to interact with backend systems" |
| Few-shot prompting | Giving LLM examples to learn from | "We use few-shot retrieval for classification" |
| Embeddings | Converting text to numerical vectors | "We embed documents for semantic search" |
| Vector store | Database optimized for similarity search | "Historical cases stored in a vector database" |
| Structured output | Forcing LLM to respond in specific format | "We enforce JSON schema for consistent downstream processing" |
| Human-in-the-loop | Human validates AI decisions | "Low-confidence predictions route to human review" |
| Hallucination | AI generating false information | "RAG grounding reduces hallucination risk" |
| Prompt engineering | Designing effective LLM instructions | "We optimized prompts for accuracy and consistency" |

---

## Final Prep Checklist

- [ ] Can walk through Architecture Diagram for each of 6 solutions
- [ ] Can explain WHY you chose this approach over alternatives
- [ ] Can describe the AWS services and their roles
- [ ] Can translate each solution to a Healthcare/CVS use case
- [ ] Know the GCP equivalents (Vertex AI, Gemini, BigQuery, GKE)
- [ ] Can discuss guardrails, especially for healthcare (HIPAA, PHI)
- [ ] Have 2-3 metrics for each solution's impact
- [ ] Can explain failure modes and how you handle them


---

## CVS Health100 — Hiring Manager Interview Preparation

### About the Role & Company

**Company:** CVS Health ($357B revenue, 300K+ employees)
**Platform:** Health100 — AI-native health technology platform
**Cloud:** Google Cloud (GCP) — Powered by Google Cloud AI
**Title:** Lead Director, Software Engineering — Health100 Platform
**Salary:** $144,200 - $288,400 base + bonus + benefits
**Reports to:** Senior Director/VP of Engineering, Health100
**Locations:** Woonsocket RI (HQ preferred), Scottsdale AZ, Hartford CT, Northbrook IL, Boston MA, Richardson TX, Remote

**What Health100 does:**
Unifies pharmacies, providers, insurers, PBMs, and digital health solutions into a single consumer-focused ecosystem. Powered by Google Cloud AI, reimagining personalized and connected health experiences.

---

### HM Interview Structure (Expected 60 min)

| Segment | Duration | What They're Assessing |
|---------|----------|----------------------|
| Intro & Role Context | 5 min | HM explains team, challenges, what they need |
| Your Background Walk-Through | 10 min | Can you tell a compelling, relevant story? |
| Technical Depth | 15 min | Do you understand distributed systems, AI, cloud? |
| Leadership & Delivery | 15 min | Can you build/scale teams and deliver at pace? |
| Stakeholder & Strategy | 10 min | Can you partner cross-functionally and communicate up? |
| Your Questions | 5 min | Are you genuinely interested and strategic? |

---

### Opening: Your 2-Minute Pitch

> "I'm a technology executive with 24+ years in software engineering and 12+ years in people leadership. Currently at Amazon, I lead a 250+ person organization driving Amazon Freight from $30M to $100M revenue — owning technical strategy, roadmap, and cross-functional delivery across 8 engineering teams and 10+ services. 
>
> Before that, I built AWS's App Dev & DevOps consulting practice from 4 to 50+ engineers in 15 months, delivering cloud-native solutions for Fortune 5000 clients. At Oracle, I managed the engineering org for a $400M+ SaaS platform.
>
> What excites me about Health100 is the AI-native architecture — I've spent the last 18 months shipping production GenAI solutions at Amazon: AI Agents, RAG-based systems, and automated workflows that handle real customer interactions. I'd love to bring that applied AI leadership plus my experience scaling engineering orgs to help Health100 deliver on its vision of connected, personalized health experiences."

---

### Technical Depth Questions & Answers

**Q1: "Tell me about a complex distributed system you've built or owned."**

**STAR Response:**
- **Situation:** Amazon Freight needed to scale from a $30M MVP to a $100M platform serving thousands of shippers, with real-time tracking, dynamic pricing, and carrier matching across 10+ microservices.
- **Task:** I owned the technical strategy and delivery for the entire platform — 8 teams, 10+ services, distributed across North America and Europe.
- **Action:** Worked with Principal Engineers to design the service architecture — event-driven (SQS/SNS), microservices on ECS, API Gateway for external integrations, DynamoDB for real-time state, Redshift for analytics. Implemented CI/CD pipelines and defined SLAs per service. Drove operational excellence with runbooks, on-call rotations, and automated alerting.
- **Result:** Scaled from $30M to $100M revenue, 48% cost reduction, 99.9% uptime on critical path services. Platform now supports $5B target by 2030.

**Key follow-up you should be ready for:** "What would you do differently?" → "I'd invest in platform engineering earlier — we built shared capabilities (auth, observability, feature flags) later than ideal. For a greenfield like Health100, I'd establish those foundations from day one."

---

**Q2: "How do you think about building an AI-native platform vs. adding AI to existing systems?"**

> "There's a fundamental architecture difference. Adding AI to existing systems means AI is a feature layer — it processes outputs from traditional systems. AI-native means AI is in the core loop — it's not just analyzing data, it's making decisions, orchestrating workflows, and directly shaping the user experience.
>
> For Health100, being AI-native means:
> 1. **Unified data layer first** — you can't have intelligent AI without connected data across pharmacy, insurance, providers, and claims
> 2. **AI as a first-class service** — with its own contracts, SLAs, monitoring, and evaluation frameworks
> 3. **Evaluation/observability built in from day one** — not retrofitted. You need to know when the AI is wrong before the user does
> 4. **Graduated autonomy** — start with AI-assist, earn trust through metrics, then expand to autonomous actions
>
> At Amazon, we added AI to existing services — it works, but you inherit constraints. For Health100's greenfield opportunity, I'd advocate for AI services that are peers to traditional services, not plugins."

---

**Q3: "This role requires GCP expertise. Your background is AWS. How do you bridge that?"**

> "The architectural patterns transfer directly — I'm not switching from horse-drawn carriages to cars, I'm switching from driving a Toyota to a Honda. The principles of distributed systems, microservices, container orchestration, and AI/ML platforms are cloud-agnostic. Specifically:
>
> - ECS/EKS → **GKE** (I've helped clients run Kubernetes at scale)
> - Bedrock → **Vertex AI + Gemini** (same patterns: model selection, RAG, agents)
> - Lambda → **Cloud Functions / Cloud Run**
> - DynamoDB → **Firestore / Bigtable**
> - Redshift → **BigQuery**
> - CloudFormation → **Terraform** (which is already multi-cloud)
>
> More importantly, at AWS ProServe I helped enterprise clients *migrate across platforms* — I understand multi-cloud architectures deeply. I'd invest the first 30 days in GCP-specific certification and hands-on work, but I can contribute immediately on architecture decisions, team leadership, and delivery execution from day one."

---

**Q4: "Describe your experience with AI/GenAI in production."**

> "I've spent 18+ months shipping production AI — not POCs, but systems handling real traffic:
>
> 1. **AI Agents for shipper support** — Built on Amazon Bedrock, these agents handle live customer inquiries using RAG for knowledge grounding and tool-use for taking actions on backend systems. They resolve 70%+ of inquiries without human intervention.
> 
> 2. **RAG-based case categorization** — Replaced manual triage with a few-shot retrieval + LLM classification pipeline. 90%+ accuracy, auto-routes high-confidence cases, flags edge cases for human review.
>
> 3. **TMS automation via AI Agents** — Multi-step agents that interact with external Transportation Management Systems autonomously — checking status, updating records, rescheduling pickups. Uses the ReAct pattern with defined tool APIs.
>
> 4. **Natural language BI** — Custom MCP servers that translate business questions into SQL queries against our data warehouse, returning data + narrative insights.
>
> 5. **AI summaries** — Automated post-contact and operational summaries using structured output from LLMs, with PII detection guardrails.
>
> The key lesson: shipping AI is 20% model work and 80% engineering — evaluation, guardrails, monitoring, graceful degradation, and human-in-the-loop design."

---

### Leadership & Delivery Questions

**Q5: "Tell me about building and scaling a high-performing engineering organization."**

**STAR Response:**
- **Situation:** At AWS ProServe, I was tasked with building a new cloud consulting practice from zero in 2019.
- **Task:** Hire, train, and operationalize a team that could deliver complex cloud engagements at 90% utilization while maintaining technical excellence.
- **Action:** 
  - Defined hiring bar: 3+ AWS certs, hands-on coding + architecture skills, client-facing communication
  - Built structured hiring pipeline: hired 30+ engineers in 15 months
  - Established delivery frameworks: engagement playbooks, reusable accelerators, peer reviews
  - Created career paths: individual contributor track and management track
  - Maintained culture: weekly tech talks, innovation sprints, internal open-source contributions
- **Result:** 4 → 50+ engineers in 15 months. 90% utilization (industry benchmark: 65-70%). 10+ concurrent enterprise engagements. Practice playbooks became templates for other GCC practices.

**Follow-up: "How did you handle underperformers?"**
> "I believe in radical candor — early, specific, actionable feedback. At Oracle, when scaling from 30 to 80, not everyone was the right fit for the cloud transformation we were driving. I implemented structured performance conversations: clear expectations, 30-day plans with measurable milestones, weekly 1:1 check-ins. About 80% improved; for the 20% who didn't, I helped them find better-fit roles internally or externally. The key is acting early — waiting helps no one."

---

**Q6: "How do you manage a portfolio of parallel initiatives with different risk profiles?"**

> "This is my daily reality at Amazon Freight. I manage simultaneously:
>
> - **Production infrastructure** — zero-tolerance for downtime, SLA-driven
> - **New product development** — fast iteration, controlled risk
> - **AI/GenAI initiatives** — high uncertainty, needs experimentation budget
> - **Compliance/audit work** — deadline-driven, non-negotiable
>
> My framework:
> 1. **Categorize by risk/urgency:** Production issues > compliance deadlines > product milestones > experimentation
> 2. **Dedicated capacity allocation:** I don't context-switch teams. Each team has a primary mission with 80% focus, 20% innovation buffer
> 3. **Different governance per type:** Production = daily standups, tight change control. Innovation = weekly demos, fail-fast sprints
> 4. **Single executive view:** I maintain one roadmap with all workstreams visible, clear dependencies, and risk flags
> 5. **Escalation clarity:** Teams know exactly when to escalate vs. decide independently
>
> For Health100, I'd apply the same approach — separate the platform reliability work from the AI innovation work with different cadences but unified visibility."

---

**Q7: "How do you work with distributed teams including offshore/nearshore?"**

> "I've managed distributed teams throughout my career — 8 ODC teams at Oracle across India, offshore + nearshore at AWS ProServe, and multi-geo teams at Amazon Freight spanning Nashville, Hyderabad, and Europe.
>
> My principles:
> - **Async-first communication:** Decisions and context documented in writing, not trapped in meetings
> - **Overlapping hours:** Require 4-hour overlap windows for collaboration; use them for design reviews and problem-solving, not status updates
> - **Ownership by team, not location:** Each team owns end-to-end outcomes. Don't split feature work across geos — that creates handoff waste
> - **Equal access to context:** Offshore teams get the same strategy context as onshore. They can't make good decisions without understanding the 'why'
> - **In-person cadence:** Quarterly in-person workshops for relationship building and complex planning
> - **Metrics-driven visibility:** Same dashboards, same velocity metrics, same quality bars regardless of location"

---

**Q8: "Tell me about a time you influenced a decision with senior leadership when there was disagreement."**

**STAR Response:**
- **Situation:** At Amazon Freight, our VP wanted to accelerate enterprise customer onboarding by reducing integration time from 6 weeks to 2 weeks. Product proposed cutting testing phases.
- **Task:** I needed to advocate for a different approach without appearing to block business velocity.
- **Action:** 
  - Quantified the risk: showed historical data that rushed integrations led to 3x more production incidents and 40% higher churn in first 90 days
  - Proposed alternative: invest in self-service integration tooling + automated validation (costing 6 weeks of engineering, saving 4 weeks per customer forever)
  - Framed as "faster AND safer" not "safer but slower"
  - Built a quick prototype to demonstrate feasibility
- **Result:** VP approved the investment. Within 3 months, integration time dropped to 10 days (better than the 2-week target) with zero increase in production incidents. Enterprise churn dropped 25%.

---

### Stakeholder & Strategy Questions

**Q9: "How would you approach your first 90 days in this role?"**

> **Days 1-30: LEARN**
> - Meet every engineering manager and senior engineer 1:1
> - Understand the current architecture, tech debt, and production health
> - Map stakeholder landscape: Product, Architecture, Security, Business, Design
> - Understand Health100's roadmap and where engineering is a bottleneck
> - Assess team health: attrition, engagement, skill gaps, hiring pipeline
> - Get hands-on with GCP/Vertex AI (certifications, tutorials, pair programming)
>
> **Days 31-60: ASSESS & QUICK WINS**
> - Identify 2-3 quick wins that build credibility (reduce deploy friction, fix top pain points)
> - Draft engineering excellence standards and share for feedback
> - Align with Senior Director on priorities, success metrics, and decision rights
> - Start 1:1 cadence with cross-functional partners (Product, Security, Architecture)
> - Assess vendor/contractor strategy — are we getting value?
>
> **Days 61-90: EXECUTE & SET DIRECTION**
> - Publish team roadmap and OKRs aligned to Health100 business outcomes
> - Implement operational frameworks (on-call, incident response, deployment standards)
> - Make first critical hiring decisions (fill gaps identified in assessment)
> - Present engineering strategy to senior leadership
> - Establish innovation cadence (AI experimentation, tech talks, hackathons)

---

**Q10: "What's your philosophy on engineering excellence and delivery governance?"**

> "Engineering excellence isn't about perfection — it's about predictable, sustainable, high-quality delivery. My framework:
>
> 1. **Define 'done' clearly:** Every feature has acceptance criteria that include: code reviewed, tested (unit + integration), documented, monitored, and operable
> 2. **Automate the guardrails:** CI/CD pipelines enforce quality — linting, testing, security scanning, performance benchmarks. If it's important, it's automated.
> 3. **Measure what matters:** 
>    - Lead time (commit → production)
>    - Deployment frequency
>    - Change failure rate
>    - Mean time to recovery
>    These DORA metrics tell you if you're actually delivering well, not just busy
> 4. **Blameless incident culture:** When things break (and they will), we run blameless retrospectives focused on systemic fixes, not individual blame
> 5. **Risk management through progressive delivery:** Feature flags, canary deployments, A/B testing. Never big-bang releases.
>
> For healthcare specifically, I'd add: **compliance-as-code** — HIPAA requirements encoded in automated checks, not manual audits."

---

### Questions YOU Should Ask the HM

Ask 3-4 of these (pick based on conversation flow):

**About the team and challenges:**
1. "What does the current engineering organization look like? How many managers report to this role, and what's the total IC count?"
2. "What's the biggest engineering challenge Health100 faces right now — is it scaling, speed of delivery, quality, talent, or something else?"
3. "How mature is the platform today? Are we building greenfield, or modernizing/integrating existing CVS systems?"

**About AI/GenAI strategy:**
4. "How central is AI to Health100's architecture today vs. your 12-month vision? What's the current gap?"
5. "What AI infrastructure exists — Vertex AI, custom models, third-party? And how does the team collaborate with Google Cloud's AI teams?"
6. "How do you handle responsible AI governance given healthcare regulations?"

**About culture and success:**
7. "What does success look like for this role in the first year? What would make you say 'this hire was a home run'?"
8. "How does Health100 operate within CVS — is it a startup-within-a-company, or more integrated with existing CVS engineering?"
9. "What's the decision-making culture like? How much autonomy does this role have on technical direction?"

**About roadmap:**
10. "What consumer experiences are you most excited about that Health100 enables in the next 12 months?"

---

### Potential Red Flags & How to Handle

| If They Say... | What It Might Mean | How to Respond |
|---|---|---|
| "We're still figuring out the roadmap" | Ambiguity, possibly chaotic | "I thrive in ambiguity — I built AWS ProServe from zero with no playbook. I'd love to help shape it." |
| "We need someone very hands-on technically" | Might expect you to code | "I'm hands-on with architecture and AI tooling. I code prototypes and review designs, but my highest leverage is setting technical direction and unblocking teams." |
| "GCP experience is really important" | They might prefer GCP-native candidates | "The patterns transfer directly. I've helped enterprises migrate across clouds. I'll invest my first 30 days in GCP depth." |
| "The team has had some turnover" | Possible morale/culture issues | "I've rebuilt teams before — at Oracle I stabilized after acquisition turmoil. What's your read on the root cause?" |
| "We move very fast" | Could mean unstaffed or rushing | "I love speed — I took a product from concept to MVP in 100 days at my startup. How do you balance speed with quality in healthcare?" |

---

### Compensation Negotiation Prep

**Role range:** $144,200 - $288,400 base
**Your target:** $250K+ total comp
**Your current:** ~$300K total (Amazon: $191K base + RSUs + bonus)

**Strategy:**
- Don't discuss comp in HM interview — say "I'm sure we can work something out if there's mutual fit"
- If pressed: "I'm currently in the $300K total comp range and would expect something competitive for a Lead Director role at CVS"
- Know that CVS also offers: annual bonus (15-25% for directors), RSUs (growing program), 401k match, HSA, ESPP
- The midpoint of their range ($216K base) + 20% bonus + equity could get you to $280-320K total

---

### Day-Before Checklist

- [ ] Re-read this entire prep guide
- [ ] Practice 2-minute pitch out loud (time it)
- [ ] Review Health100 + Google Cloud partnership news (search recent press)
- [ ] Review CVS Health Q1/Q2 2026 earnings for business context
- [ ] Have 4 questions ready (memorized, not read)
- [ ] Test video/audio setup
- [ ] Have water, notebook, and pen ready
- [ ] Review architecture diagrams — can you draw them from memory?
- [ ] Know your key numbers cold: 250+ org, $30M→$100M, 48% cost reduction, 4→50+ in 15 months, 30→80 engineers


---

# PART 2: PRACTICAL PREPARATION PROGRAM

> This is your hands-on curriculum to build real, demonstrable skills — not just talk about them. Each section has learning content PLUS working labs you can execute. The goal: walk into any interview able to whiteboard architecture, discuss real trade-offs, and prove you've actually built things.

---

## People Management Preparation

> 📺 **Watch:** [Intro to Architecture & Systems Design Interviews](https://www.youtube.com/watch?v=ZgdS0EUmn70) (Jackson Gabbard) — how senior technical interviews are actually evaluated

The CVS role is fundamentally a people leadership role: *"Lead, mentor, and grow engineering managers and senior engineers, owning hiring, performance management, career development, succession planning."* You manage managers — this is second-line leadership.

### Core Frameworks to Master

**1. The Manager-of-Managers Shift**

At this level, you're not managing engineers — you're managing the *managers* who manage engineers. Your leverage changes:

| First-Line Manager | Second-Line Manager (This Role) |
|---|---|
| Coaches individual engineers | Coaches managers on how to coach |
| Owns team delivery | Owns multi-team strategy & outcomes |
| Reviews code/designs | Reviews architecture & technical direction |
| Runs 1:1s with ICs | Runs 1:1s with managers, skip-levels with ICs |
| Tactical execution | Organizational design & scaling |

**Talking point:** *"As a manager of managers, my job is to multiply through my leaders. I set clear outcomes and standards, then give my managers the autonomy to execute. I use skip-level 1:1s to stay connected to the ground truth without undermining my managers."*

**2. Situational Leadership Model**

Adapt your style to the person and situation:
- **Directing** (new/struggling): High direction, high support
- **Coaching** (developing): High direction, building skills
- **Supporting** (competent but low confidence): Low direction, high support
- **Delegating** (high performers): Low direction, low support — get out of their way

**3. The GROW Coaching Model** (for developing your managers)
- **Goal:** What do you want to achieve?
- **Reality:** What's the current situation?
- **Options:** What could you do?
- **Will:** What will you commit to?

**4. Radical Candor** (Kim Scott)
- Care Personally + Challenge Directly
- Avoid "Ruinous Empathy" (caring but not challenging = kindness that hurts)
- Avoid "Obnoxious Aggression" (challenging without caring)

### Behavioral Questions — People Management (with STAR answers)

**Q: "How do you develop and grow engineering managers?"**

**STAR:**
- **Situation:** At Amazon Freight, I inherited managers of varying experience — some first-time managers promoted from strong ICs.
- **Task:** Level them up to run autonomous, high-performing teams.
- **Action:**
  - Weekly 1:1s focused on *their* growth, not just status ("What's the hardest decision you made this week?")
  - Paired new managers with experienced mentors
  - Gave stretch assignments with a safety net (I'd review, but they'd own)
  - Taught them frameworks: how to run effective 1:1s, give feedback, handle underperformance
  - Created a manager forum for peer learning
- **Result:** 2 first-time managers grew into senior managers within 18 months; team engagement scores improved; I could delegate increasingly complex initiatives.

**Q: "Tell me about a time you had to manage out an underperformer."**

**STAR:**
- **Situation:** A senior engineer at Oracle was technically strong but consistently missed commitments and created friction with the team.
- **Task:** Address the performance and behavior issues fairly.
- **Action:**
  - Direct, specific feedback with examples (not vague)
  - Co-created a 60-day improvement plan with measurable goals
  - Weekly check-ins with documented progress
  - Made clear the consequences and the support available
- **Result:** Performance didn't improve to the bar despite support. I transitioned them out respectfully with dignity. The team's velocity and morale improved measurably. Key learning: acting decisively but humanely is a kindness to the whole team.

**Q: "How do you handle succession planning?"**

> "I maintain a talent matrix for my org — who's ready now, ready in 1 year, ready in 2 years for each critical role. For every key position, I want at least one identified successor being actively developed. I give high-potentials stretch assignments and visibility to senior leadership. I also document tribal knowledge so no single person is a bus-factor risk. At Amazon, I ensured every team had a clear #2 who could step up."

**Q: "How do you build culture across distributed teams?"**

> "Culture is what people do when you're not watching. I build it through: clear values made concrete in decisions, celebrating the right behaviors publicly, consistent rituals (demos, retros, tech talks), psychological safety so people speak up, and leading by example. For distributed teams, I over-invest in written communication and periodic in-person gatherings for relationship-building."

**Q: "How do you give difficult feedback?"**

> "I use the SBI model — Situation, Behavior, Impact. 'In yesterday's design review (situation), when you dismissed the junior engineer's idea before they finished (behavior), it shut down the discussion and I noticed others held back (impact).' Specific, timely, focused on behavior not character. Then I listen and we problem-solve together. I give feedback early and often so it's never a surprise."

### People Management Scenarios to Rehearse

1. **Two of your managers are in conflict over resource allocation.** → Facilitate, don't dictate. Get them to align on shared goals first, then negotiate trade-offs with data.

2. **A high performer threatens to quit over comp.** → Understand the real driver (often not just money). Advocate hard if they're critical, but never make retention counter-offers a habit.

3. **Your best engineer wants to become a manager, but you think they're better as an IC.** → Create a tech-lead path. Be honest about what management really involves. Let them try with support.

4. **A team is burning out from on-call load.** → Root-cause the alert volume. Invest in reliability. Rebalance rotations. This is an operational excellence issue, not a people issue alone.

5. **You need to cut 15% of budget.** → Protect your best people, be transparent about the why, cut projects not just people, communicate with empathy.

---

## AI Infrastructure Preparation

> 📺 **Watch:** [Integrating Foundation Models with Amazon Bedrock](https://www.youtube.com/watch?v=ab1mbj0acDo) (AWS Developers) · 🎓 [AWS GenAI Learning Plan](https://explore.skillbuilder.aws/learn/public/learning_plan/view/2068/generative-ai-learning-plan-for-developers) (free) · 🧪 [Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop)

The role wants: *"Strong technical depth in distributed systems and cloud-native architectures, including microservices, DevOps (CI/CD, Kubernetes/Docker), and cloud platforms."* Plus AI infrastructure for an AI-native platform.

### AI Infrastructure Stack — What You Must Understand

**Layer 1: Compute & Orchestration**
```
┌─────────────────────────────────────────┐
│  Model Serving Infrastructure            │
│  • GPU/TPU clusters for inference        │
│  • Auto-scaling based on request load    │
│  • Model versioning & A/B testing        │
│  Examples: SageMaker Endpoints,          │
│  Vertex AI Endpoints, GKE + GPU nodes    │
└─────────────────────────────────────────┘
```

**Layer 2: Model Access & Gateway**
```
┌─────────────────────────────────────────┐
│  LLM Gateway / API Layer                 │
│  • Rate limiting & quota management      │
│  • Model routing (cheap vs. powerful)    │
│  • Caching (semantic cache)              │
│  • Cost tracking per team/use case       │
│  • Fallback & retry logic                │
│  Examples: Bedrock, Vertex AI, LiteLLM   │
└─────────────────────────────────────────┘
```

**Layer 3: RAG & Knowledge Infrastructure**
```
┌─────────────────────────────────────────┐
│  Vector Database & Retrieval             │
│  • Embedding pipeline (batch + realtime) │
│  • Vector store (OpenSearch, Pinecone,   │
│    pgvector, Vertex Vector Search)       │
│  • Chunking & indexing strategy          │
│  • Hybrid search (vector + keyword)      │
│  • Re-ranking                            │
└─────────────────────────────────────────┘
```

**Layer 4: Orchestration & Agents**
```
┌─────────────────────────────────────────┐
│  Agent Orchestration                     │
│  • Workflow engine (Step Functions,      │
│    LangGraph, Bedrock Agents)            │
│  • Tool/function registry                │
│  • State management                      │
│  • Multi-agent coordination              │
└─────────────────────────────────────────┘
```

**Layer 5: Evaluation & Observability**
```
┌─────────────────────────────────────────┐
│  MLOps / LLMOps                          │
│  • Prompt versioning & management        │
│  • Evaluation pipelines (accuracy,       │
│    hallucination, latency, cost)         │
│  • Monitoring & alerting                 │
│  • Feedback loops (human ratings)        │
│  • Drift detection                       │
└─────────────────────────────────────────┘
```

**Layer 6: Governance & Safety**
```
┌─────────────────────────────────────────┐
│  Responsible AI Layer                    │
│  • Guardrails (PII/PHI, toxicity, bias)  │
│  • Content filtering                     │
│  • Audit logging                         │
│  • Access controls (who can call what)   │
│  • Compliance (HIPAA for healthcare)     │
└─────────────────────────────────────────┘
```

### Key AI Infrastructure Concepts to Discuss Fluently

**Inference optimization:**
- **Batching:** Group requests to maximize GPU utilization
- **Quantization:** Reduce model precision (FP16/INT8) for faster/cheaper inference
- **Model distillation:** Train smaller models from larger ones
- **Caching:** Semantic caching for repeated/similar queries (huge cost savings)
- **Model routing:** Use cheap models for easy tasks, expensive for hard ones

**Cost management (critical for leaders):**
- Token costs add up fast at scale — a chatbot handling 1M conversations/day can cost $100K+/month
- Strategies: caching, model routing, prompt optimization (shorter prompts), batch processing
- **Talking point:** *"AI cost governance is a real discipline. At scale, the difference between a naive implementation and an optimized one can be 10x. I'd implement per-team cost tracking, semantic caching, and tiered model routing."*

**Scaling patterns:**
- Async processing for non-realtime (queues + workers)
- Streaming responses for better UX (don't wait for full generation)
- Provisioned throughput for predictable workloads, on-demand for spiky

**Healthcare-specific infrastructure:**
- All AI processing in HIPAA-eligible services with BAA
- PHI de-identification before any model processing
- Data residency and encryption at rest/in transit
- Audit trails for every AI decision touching patient data
- Human-in-the-loop for clinical decisions

### AI Infrastructure Interview Questions

**Q: "How would you architect the AI infrastructure for Health100 to scale to millions of members?"**

> "I'd design in layers. At the base, a model gateway that abstracts the LLM provider (Vertex AI/Gemini) with built-in rate limiting, semantic caching, and cost tracking. Above that, a RAG layer with a managed vector store for member context and clinical knowledge. Then an agent orchestration layer for multi-step workflows. Critically, an evaluation/observability layer from day one — we need to catch AI errors before members do. And wrapping everything, a governance layer with PHI guardrails and audit logging for HIPAA. For scale, async processing for non-realtime tasks, streaming for chat UX, and aggressive semantic caching since many member questions repeat."

**Q: "How do you control AI costs at scale?"**

> "Four levers: First, semantic caching — many queries are similar, so cache embeddings and responses. Second, model routing — use small/cheap models for simple classification, reserve powerful models for complex reasoning. Third, prompt optimization — every token costs money, so tight prompts matter at scale. Fourth, per-team cost attribution so teams own their spend. I'd set up dashboards tracking cost-per-interaction and alert on anomalies."

---

## AI-Assisted Coding Preparation

> 📺 **Watch:** [Let's build GPT: from scratch, in code](https://www.youtube.com/watch?v=kCc8FmEb1nY) (Karpathy) — builds the intuition to *review* AI-generated code, not just accept it

Preferred qualification: *"Familiarity with tools such as Claude and Cursor, and the ability to apply them responsibly to improve speed and quality."* The role wants a leader who models modern AI-assisted development.

### The Modern AI-Assisted Development Landscape

| Tool | What It Does | Your Angle |
|------|--------------|------------|
| **Amazon Q Developer** | AI coding assistant in IDE (your experience) | "I use Amazon Q for code generation, review, and modernization" |
| **Kiro** | Agentic IDE / spec-driven development (your experience) | "I use Kiro for spec-to-code workflows" |
| **GitHub Copilot** | Inline code completion | Know it exists, industry standard |
| **Cursor** | AI-native code editor | The role mentions this — worth trying |
| **Claude Code / Codex** | Agentic coding in terminal | Terminal-based agentic dev |

### How AI-Assisted Coding Changes Engineering (Leadership View)

**Productivity gains:**
- Boilerplate/scaffolding: 5-10x faster
- Test generation: massive time savings
- Code review: AI catches issues before human review
- Documentation: auto-generated and kept current
- Legacy modernization: AI translates/refactors old code

**What leaders must manage:**
- **Quality gates:** AI-generated code still needs review, testing, security scanning
- **Over-reliance risk:** Junior engineers may not learn fundamentals
- **Security:** AI can suggest vulnerable code or leak secrets
- **IP/licensing:** Ensure generated code doesn't violate licenses
- **Consistency:** AI output must follow team standards

**Talking point:** *"AI-assisted coding is a force multiplier, but it shifts the engineer's job from writing code to specifying, reviewing, and integrating. I'd establish standards: AI accelerates, but humans own quality. I'd measure impact through DORA metrics and ensure our juniors still build deep understanding, not just prompt-and-paste."*

### AI-Assisted Coding Interview Questions

**Q: "How do you think about AI-assisted development on your teams?"**

> "I'm a strong advocate — I use these tools myself with Amazon Q and Kiro. But adoption needs guardrails. First, AI accelerates but doesn't replace judgment — all AI code goes through the same review, test, and security gates. Second, I worry about juniors not learning fundamentals, so I pair AI use with mentorship. Third, security matters — AI can suggest vulnerable patterns or leak secrets, so we scan everything. Done right, I've seen 30-40% productivity gains on boilerplate and testing. The engineer's role elevates from writing every line to architecting, specifying, and validating."

**Q: "How would you measure the impact of AI coding tools?"**

> "I'd use DORA metrics as the baseline — lead time, deployment frequency, change failure rate, MTTR. Then AI-specific measures: % of code AI-assisted, time saved on common tasks, developer satisfaction. But I'd watch for false productivity — more code isn't better if quality drops. The real metric is sustainable delivery velocity with maintained or improved quality."

---

## THE HANDS-ON LEARNING PROGRAM

> Talk is cheap. Here's your practical curriculum to actually BUILD these skills. Each lab is a working session you execute in your DevSpace. By the end, you can honestly say "I built this" — and walk through real code.

### Learning Path Overview (4-Week Program)

| Week | Focus | Labs | Outcome |
|------|-------|------|---------|
| 1 | RAG Fundamentals | Lab 1: Build a RAG system | Understand embeddings, vector search, grounding |
| 2 | AI Agents | Lab 2: Build an agent with tools | Understand ReAct, tool-use, orchestration |
| 3 | AI-Assisted Coding | Lab 3: Ship a feature with AI | Experience modern dev workflow |
| 4 | AI Infrastructure | Lab 4: Deploy & observe | Understand serving, cost, monitoring |
| 5 | Frameworks | Lab 5: HuggingFace, LangChain | Know the ecosystem & framework trade-offs |
| 6 | MCP Servers | Lab 6: Build & launch an MCP server | Understand MCP protocol & tool servers |

> 🎥 **Watch-then-build:** every lab below links to its videos, and the full curated catalog with a 6-week study plan is in [Learning Videos & Courses](#learning-videos-courses) at the end of this page.

### How to Use the Labs

All labs are in this GitHub repository under [`labs/`](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs). Each lab has a `README.md` with learning objectives, runnable code, and "interview talking points."

**Direct links to each lab:**

| Lab | Topic | Repo Link |
|-----|-------|-----------|
| Lab 1 | RAG System from scratch | [labs/lab1_rag](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab1_rag) |
| Lab 2 | AI Agent (ReAct + tools) | [labs/lab2_agent](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab2_agent) |
| Lab 3 | Ship a feature with AI | [labs/lab3_ai_coding](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab3_ai_coding) |
| Lab 4 | AI Infrastructure (cache/cost) | [labs/lab4_infra](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab4_infra) |
| Lab 5 | Frameworks (HuggingFace, LangChain) | [labs/lab5_frameworks](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab5_frameworks) |
| Lab 6 | Build & launch an MCP server | [labs/lab6_mcp](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab6_mcp) |

To run locally: `git clone https://github.com/naramsettisiva/genAIPrepration.git`, then `cd genAIPrepration/labs/lab1_rag && pip install -r requirements.txt && python3 rag_demo.py`

### Lab 1: Build a RAG System (Week 1)

> 📺 [What is RAG?](https://www.youtube.com/watch?v=T-D1OfcDW1M) · [Learn RAG From Scratch](https://www.youtube.com/watch?v=sVcwVQRHIc8) · [Transformers explained](https://www.youtube.com/watch?v=wjZofJX0v4M)

**What you'll build:** A working retrieval-augmented Q&A system over a set of documents.

**You'll learn:**
- How embeddings turn text into vectors
- How vector similarity search works
- How RAG grounds LLM responses in your data
- Why chunking strategy matters

**Concepts demonstrated:** Embeddings, vector stores, semantic search, prompt construction, grounding

### Lab 2: Build an AI Agent (Week 2)

> 📺 [What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI) · [Andrew Ng on agentic workflows](https://www.youtube.com/watch?v=sal78ACtGTc)

**What you'll build:** An agent that answers questions AND takes actions using tools.

**You'll learn:**
- The ReAct pattern (Reason + Act)
- How to define and register tools
- How agents decide which tool to call
- Guardrails and error handling

**Concepts demonstrated:** Agentic AI, tool-use/function calling, multi-step reasoning

### Lab 3: Ship a Feature with AI-Assisted Coding (Week 3)

> 📺 [Let's build GPT, in code](https://www.youtube.com/watch?v=kCc8FmEb1nY) (Karpathy)

**What you'll build:** A small full-stack feature using AI coding tools end-to-end.

**You'll learn:**
- Spec-driven development workflow
- How to prompt effectively for code
- How to review and validate AI-generated code
- The quality gates that matter

**Concepts demonstrated:** Modern AI dev workflow, code review discipline, testing

### Lab 4: AI Infrastructure — Deploy & Observe (Week 4)

> 📺 [Amazon Bedrock in your code](https://www.youtube.com/watch?v=ab1mbj0acDo) · 🧪 [Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop)

**What you'll build:** Deploy a model endpoint with monitoring, caching, and cost tracking.

**You'll learn:**
- Model serving patterns
- Semantic caching for cost reduction
- Observability and evaluation
- Scaling considerations

**Concepts demonstrated:** MLOps/LLMOps, cost optimization, production readiness

### Lab 5: Popular Frameworks & Patterns (HuggingFace, LangChain, LlamaIndex)

> 📺 [LangChain vs LangGraph](https://www.youtube.com/watch?v=qAF1NjEVHhY) · 🎓 [HuggingFace LLM Course](https://huggingface.co/learn/llm-course) · [HF Agents Course](https://huggingface.co/learn/agents-course)

**What you'll build:** Run real HuggingFace models locally + explore LangChain patterns.

**You'll learn:**
- The framework ecosystem and when to use each
- Running open models yourself (critical for PHI/HIPAA)
- Zero-shot classification (categorize WITHOUT training data)
- LangChain patterns: chains, RAG, agents, memory
- Build-vs-buy-vs-framework leadership judgment

**Concepts demonstrated:** HuggingFace transformers, LangChain, LlamaIndex, framework trade-offs

**Runnable examples (real models, no API key):**
- Sentiment analysis → member/shipper satisfaction routing
- Zero-shot classification → case categorization with no training data
- Summarization → AI post-contact summaries
- NER → PII/PHI detection for HIPAA redaction

**Interview power line:** *"I self-host open models via HuggingFace when data can't leave our boundary — critical for PHI. I use LangChain/LlamaIndex to accelerate standard RAG and agent patterns, but drop to the raw cloud SDK for high-scale production paths. The judgment is always: does the framework earn its place without hiding what matters?"*

### Lab 6: Build & Launch an MCP Server

> 📺 [What is MCP?](https://www.youtube.com/watch?v=eur8dUO9mvE) · [MCP full workshop (Anthropic)](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) · 📄 [MCP docs](https://modelcontextprotocol.io/docs/getting-started/intro)

**What you'll build:** A real, working MCP (Model Context Protocol) server that AI assistants can connect to.

**You'll learn:**
- What MCP is ("USB-C for AI") and why it matters
- The MCP protocol: JSON-RPC over stdio — initialize, tools/list, tools/call
- How to launch an MCP server and connect it to Claude Desktop / Amazon Q
- The production SDK (FastMCP) approach
- Security: auth, least privilege, input validation, audit logging

**Concepts demonstrated:** MCP protocol, tool servers, stdio transport, AI-to-tools integration

**Runnable:** `mcp_server.py` (real protocol implementation) + `test_client.py` (drives the full conversation) — exposes business metrics so an AI can answer BI questions by calling your server.

**Interview power line:** *"I built and launched an MCP server from scratch — it's the open standard that lets any AI assistant connect to your tools uniformly. Under the hood it's JSON-RPC over stdio with initialize, tools/list, and tools/call. I implemented the protocol by hand so I understand exactly what happens, which matters for debugging, security, and auth."*

---

## Interview Practice Sessions

Beyond the technical labs, rehearse these with me (I can role-play the interviewer):

1. **Mock HM Interview** — I play the CVS hiring manager, you answer live
2. **Whiteboard Architecture** — I give you a design prompt, you walk through it
3. **Behavioral Deep-Dive** — Rapid-fire STAR questions on leadership
4. **Technical Grilling** — I probe your GenAI/infrastructure depth
5. **Reverse Interview** — Practice the questions YOU ask

Just say "mock interview" or "whiteboard practice" and I'll run a session.

---

## 🎥 Learning Videos & Courses

A curated study path that maps directly to the [labs](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/) and
[AWS solutions](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/) in this repo.

> **All links in this file were verified as live.** YouTube entries were validated via the
> oEmbed API (titles below are the real, returned titles). Courses/docs were checked for a
> 200 response. If a link ever rots, use the channel/search links at the bottom.

**Suggested pace:** ~1 topic per week alongside the matching lab. Watch → then build.

---

### 1. LLM Foundations
*Watch before Lab 1. Builds the mental model for everything else.*

| Video | Author | Why watch |
|-------|--------|-----------|
| [Large Language Models explained briefly](https://www.youtube.com/watch?v=LPZh9BOjkQs) | 3Blue1Brown | Best short, visual intro (~7 min) |
| [[1hr Talk] Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) | Andrej Karpathy | The single best executive-level overview |
| [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) | Andrej Karpathy | Long-form deep dive: pretraining → RLHF |
| [Transformers, the tech behind LLMs (Ch 5)](https://www.youtube.com/watch?v=wjZofJX0v4M) | 3Blue1Brown | Visual explanation of transformer architecture |
| [Attention in transformers, step-by-step (Ch 6)](https://www.youtube.com/watch?v=eMlx5fFNoYc) | 3Blue1Brown | Understand attention — the core mechanism |
| [Introduction to large language models](https://www.youtube.com/watch?v=zizonToFXDs) | Google Cloud Tech | Vendor-neutral framing; useful GCP context |
| [Let's build GPT: from scratch, in code](https://www.youtube.com/watch?v=kCc8FmEb1nY) | Andrej Karpathy | Optional/deep: code a transformer line by line |

**Interview payoff:** you can explain what an LLM actually does, why it hallucinates, and what attention means — without hand-waving.

---

### 2. RAG (Retrieval-Augmented Generation)
*Pairs with → [Lab 1: RAG](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab1_rag/) and [Solution 1](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/01_ai_customer_support/) / [Solution 2](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/02_case_categorization/)*

| Video | Author | Why watch |
|-------|--------|-----------|
| [What is Retrieval-Augmented Generation (RAG)?](https://www.youtube.com/watch?v=T-D1OfcDW1M) | IBM Technology | Crisp ~7 min conceptual explainer |
| [Learn RAG From Scratch – Python AI Tutorial](https://www.youtube.com/watch?v=sVcwVQRHIc8) | freeCodeCamp (LangChain engineer) | Full hands-on course; mirrors Lab 1 |

**Interview payoff:** chunking trade-offs, embeddings, vector search, grounding to reduce hallucination.

---

### 3. AI Agents & Tool Use
*Pairs with → [Lab 2: Agent](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab2_agent/) and [Solution 4](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/04_tms_agent/)*

| Video | Author | Why watch |
|-------|--------|-----------|
| [What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI) | IBM Technology | Clear definition: agents vs. chatbots |
| [What's next for AI agentic workflows — Andrew Ng](https://www.youtube.com/watch?v=sal78ACtGTc) | Sequoia Capital | Strategic/leadership view of agentic AI |
| [LangChain vs LangGraph: A Tale of Two Frameworks](https://www.youtube.com/watch?v=qAF1NjEVHhY) | IBM Technology | When to use which — a real architecture decision |

**Interview payoff:** ReAct pattern, tool/function calling, when agents beat simple chains, guardrails on write actions.

---

### 4. MCP (Model Context Protocol)
*Pairs with → [Lab 6: MCP Server](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab6_mcp/)*

| Video | Author | Why watch |
|-------|--------|-----------|
| [What is MCP? Integrate AI Agents with Databases & APIs](https://www.youtube.com/watch?v=eur8dUO9mvE) | IBM Technology | Short conceptual intro |
| [Why MCP really is a big deal](https://www.youtube.com/watch?v=FLpS7OfD5-s) | Confluent Developer | Why it matters architecturally (N×M problem) |
| [Building Agents with MCP — Full Workshop](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) | AI Engineer (w/ Anthropic) | Deep, practical workshop from the source |

📄 Docs: [MCP official documentation](https://modelcontextprotocol.io/docs/getting-started/intro)

**Interview payoff:** explain MCP as "USB-C for AI," describe initialize/tools-list/tools-call, and discuss auth + least privilege.

---

### 5. AWS Bedrock & AI Infrastructure
*Pairs with → all [AWS solutions](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/) and [Lab 4: AI Infra](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab4_infra/)*

| Resource | Type | Why |
|----------|------|-----|
| [Integrating Foundation Models into Your Code with Amazon Bedrock](https://www.youtube.com/watch?v=ab1mbj0acDo) | Video (AWS Developers) | Hands-on Bedrock SDK usage |
| [Generative AI Learning Plan for Developers](https://explore.skillbuilder.aws/learn/public/learning_plan/view/2068/generative-ai-learning-plan-for-developers) | AWS Skill Builder (free) | Official structured AWS path |
| [Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop) | Hands-on labs (AWS Samples) | Best practical Bedrock repo |
| [AWS Workshop Catalog](https://catalog.workshops.aws) | Workshops | Search "Bedrock", "GenAI", "Agents" |
| [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) | Docs | Authoritative reference |
| [Bedrock Agents](https://aws.amazon.com/bedrock/agents/) | Docs | Agents + Action Groups concepts |
| [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/) | Blog | Reference architectures & new features |

**Interview payoff:** name the services, explain the layers (gateway → RAG → agents → eval → governance), and talk cost levers (caching, model routing).

---

### 6. Frameworks: HuggingFace, LangChain
*Pairs with → [Lab 5: Frameworks](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab5_frameworks/)*

| Resource | Type | Why |
|----------|------|-----|
| [HuggingFace LLM Course](https://huggingface.co/learn/llm-course) | Free course | Transformers, fine-tuning, running models yourself |
| [HuggingFace Agents Course](https://huggingface.co/learn/agents-course) | Free course | Build agents end-to-end |
| [HuggingFace channel](https://www.youtube.com/@HuggingFace) | YouTube | Model releases & tutorials |
| [LangChain channel](https://www.youtube.com/@LangChain) | YouTube | Patterns straight from the maintainers |

**Interview payoff:** the build-vs-buy-vs-framework judgment, and *why self-hosting matters for PHI/regulated data*.

---

### 7. Structured Learning Paths (hands-on)

Ranked by **how much you actually build**. Prefer A and B — they involve real code/labs.

#### A. AWS-native, free, most hands-on ⭐ start here

| Path | What you build | Cost |
|------|----------------|------|
| [Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop) (AWS Samples) | Real notebooks: RAG, agents, summarization, guardrails on Bedrock | Free (AWS usage only) |
| [GenAI on AWS Workshop](https://catalog.workshops.aws/genai-on-aws/en-US) | Guided end-to-end GenAI build in your own account | Free |
| [Generative AI Learning Plan for Developers](https://explore.skillbuilder.aws/learn/public/learning_plan/view/2068/generative-ai-learning-plan-for-developers) | Official AWS path w/ labs + assessments | Free |
| [AWS Workshop Catalog](https://catalog.workshops.aws) | Search "Bedrock", "Agents", "RAG" for more labs | Free |
| [AWS Skill Builder — GenAI catalog](https://explore.skillbuilder.aws/learn/external-ecommerce;view=none;redirectURL=?ctldoc-catalog-0=se-%22generative%20ai%22) | Browse all AWS GenAI training | Free tier |
| [AWS GenAI training hub](https://aws.amazon.com/training/learn-about/generative-ai/) | Role-based AWS learning paths | Free |

#### B. DeepLearning.AI short courses (1-2 hrs each, hands-on notebooks) ⭐ best value

Every course is a Jupyter notebook you actually run. These map 1:1 to this repo's labs:

| Course | Maps to |
|--------|---------|
| [Serverless LLM Apps with Amazon Bedrock](https://www.deeplearning.ai/courses/serverless-llm-apps-amazon-bedrock) | [Solution 1](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/01_ai_customer_support/) & [3](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/03_ai_summaries/) |
| [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag) | [Lab 1: RAG](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab1_rag/) |
| [Building Applications with Vector Databases](https://www.deeplearning.ai/courses/building-applications-vector-databases) | [Lab 1: RAG](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab1_rag/) |
| [Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/courses/functions-tools-agents-langchain) | [Lab 2: Agent](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab2_agent/) |
| [AI Agents in LangGraph](https://www.deeplearning.ai/courses/ai-agents-in-langgraph) | [Lab 2](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab2_agent/) & [Lab 5](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab5_frameworks/) |
| [MCP: Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) | [Lab 6: MCP](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab6_mcp/) ⭐ |
| [LangChain: Chat with Your Data](https://www.deeplearning.ai/courses/langchain-chat-with-your-data) | [Lab 5: Frameworks](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab5_frameworks/) |
| [ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/courses/chatgpt-prompt-eng) | All solutions |
| [Prompt Engineering with Llama](https://www.deeplearning.ai/courses/prompt-engineering-with-llama-2) | [Lab 5](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab5_frameworks/) |
| [Browse all courses](https://www.deeplearning.ai/courses) | — |

#### C. Coursera paths (graded labs + certificates)

| Path | Type | Why |
|------|------|-----|
| [Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms) | Course (AWS + DeepLearning.AI) | ⭐ Best AWS-aligned; hands-on labs in AWS |
| [IBM Generative AI Engineering](https://www.coursera.org/professional-certificates/ibm-generative-ai-engineering) | Professional Certificate | Deep, project-heavy, resume-bearing |
| [IBM AI Engineer](https://www.coursera.org/professional-certificates/ai-engineer) | Professional Certificate | Broader ML + GenAI engineering |
| [Generative AI Engineering with LLMs](https://www.coursera.org/specializations/generative-ai-engineering-with-llms) | Specialization | RAG, agents, fine-tuning with labs |
| [Generative AI for Everyone](https://www.coursera.org/learn/generative-ai-for-everyone) | Course (Andrew Ng) | Leadership/strategy framing |
| [Prompt Engineering](https://www.coursera.org/learn/prompt-engineering) | Course | Practical prompt craft |
| [Introduction to Large Language Models](https://www.coursera.org/learn/introduction-to-large-language-models) | Course (Google Cloud) | GCP-flavored fundamentals |
| [AWS Cloud Technical Essentials](https://www.coursera.org/learn/aws-cloud-technical-essentials) | Course | AWS foundation if you need it |
| [Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning) | Specialization | Optional deep theory |
| [Browse GenAI catalog](https://www.coursera.org/courses?query=generative%20ai) | — | Find more by depth/vendor |

#### D. Udemy & other platforms

⚠️ **Note:** Udemy blocks automated link checking, so unlike every other link in this file I
could **not** verify specific Udemy course URLs. Individual Udemy courses also get unpublished
often. Use these **search links** instead — they stay valid and show current top-rated courses:

- [Udemy — Amazon Bedrock](https://www.udemy.com/courses/search/?q=amazon%20bedrock)
- [Udemy — LangChain](https://www.udemy.com/courses/search/?q=langchain)
- [Udemy — Generative AI / LLM engineering](https://www.udemy.com/courses/search/?q=generative%20ai%20llm)
- [Udemy — AWS Certified AI Practitioner](https://www.udemy.com/courses/search/?q=aws%20certified%20ai%20practitioner)

When choosing on Udemy, filter for **4.5+ rating, updated within 6 months, and "hands-on
projects"** in the curriculum — many GenAI courses go stale fast.

Also worth a look: [Pluralsight paths](https://www.pluralsight.com/paths) ·
[A Cloud Guru](https://acloudguru.com) (strong on AWS labs)

#### Recommended sequence (if you only do three things)

1. **[Serverless LLM Apps with Amazon Bedrock](https://www.deeplearning.ai/courses/serverless-llm-apps-amazon-bedrock)** — ~1.5 hrs, gets you building on Bedrock immediately
2. **[Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop)** — the most practical AWS-native hands-on repo
3. **[Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms)** — the depth + credential

---

### 8. Engineering Leadership & Interview Craft
*For the people-management and architecture-whiteboard portions of senior interviews.*

| Video | Author | Why watch |
|-------|--------|-----------|
| [Intro to Architecture and Systems Design Interviews](https://www.youtube.com/watch?v=ZgdS0EUmn70) | Jackson Gabbard (ex-Facebook) | ⭐ How senior design interviews are actually evaluated |
| [System Design Interview – Step By Step Guide](https://www.youtube.com/watch?v=bUHFg8CZFws) | System Design Interview | Repeatable framework for whiteboarding |
| [System Design Introduction For Interview](https://www.youtube.com/watch?v=UzLMhqg3_Wc) | Tushar Roy | Fundamentals refresher |

**Interview payoff:** a repeatable structure for "design an AI-native platform" prompts.

---

### Channels Worth Subscribing To

| Channel | Focus |
|---------|-------|
| [@amazonwebservices](https://www.youtube.com/@amazonwebservices) | AWS product & how-to |
| [@AWSEventsChannel](https://www.youtube.com/@AWSEventsChannel) | re:Invent / summit deep dives |
| [@anthropic-ai](https://www.youtube.com/@anthropic-ai) | Claude, MCP, agents from the source |
| [@AndrejKarpathy](https://www.youtube.com/@AndrejKarpathy) | Best-in-class LLM education |
| [@3blue1brown](https://www.youtube.com/@3blue1brown) | Visual math behind transformers |
| [@freecodecamp](https://www.youtube.com/@freecodecamp) | Long-form free courses |
| [@HuggingFace](https://www.youtube.com/@HuggingFace) | Open models |
| [@LangChain](https://www.youtube.com/@LangChain) | Framework patterns |

**Topic searches (never go stale):**
[Bedrock Knowledge Bases + RAG](https://www.youtube.com/results?search_query=amazon+bedrock+knowledge+bases+rag) ·
[Bedrock Agents on AWS Events](https://www.youtube.com/@AWSEventsChannel/search?query=bedrock%20agents)

---

### 📅 Suggested 6-Week Study Plan

| Week | Watch | Course (hands-on) | Then build |
|------|-------|-------------------|-----------|
| 1 | LLM Foundations (§1) | [Prompt Engineering for Devs](https://www.deeplearning.ai/courses/chatgpt-prompt-eng) | [Lab 1: RAG](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab1_rag/) |
| 2 | RAG (§2) | [Advanced RAG](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag) | [Solution 2](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/02_case_categorization/) |
| 3 | Agents (§3) | [Functions, Tools & Agents](https://www.deeplearning.ai/courses/functions-tools-agents-langchain) | [Lab 2](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab2_agent/) + [Solution 4](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/04_tms_agent/) |
| 4 | Bedrock & Infra (§5) | [Serverless LLM Apps w/ Bedrock](https://www.deeplearning.ai/courses/serverless-llm-apps-amazon-bedrock) ⭐ | [Lab 4](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab4_infra/) + [Solution 1](https://github.com/naramsettisiva/genAIPrepration/tree/main/aws_solutions/01_ai_customer_support/) |
| 5 | MCP (§4) + Frameworks (§6) | [MCP with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) ⭐ | [Lab 6](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab6_mcp/) + [Lab 5](https://github.com/naramsettisiva/genAIPrepration/tree/main/labs/lab5_frameworks/) |
| 6 | Leadership & Interview Craft (§8) | [Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms) (ongoing) | Whiteboard + mock interviews |

**Rule of thumb:** never watch more than ~2 hours without building something. Retention comes from the build, not the video.
