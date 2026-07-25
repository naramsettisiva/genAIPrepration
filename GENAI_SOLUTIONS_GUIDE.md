# GenAI Solutions Guide — Architecture Patterns & Practical Program

> A cloud-agnostic guide to building production GenAI systems: six common solution
> patterns with reference architectures, plus practical sections on AI infrastructure,
> AI-assisted coding, and popular frameworks. Examples use AWS (Bedrock) with GCP
> (Vertex AI) equivalents noted throughout. All data shown is synthetic/sample.

## 1. AI-Powered Customer Support (→ Amazon Connect + Bedrock Agents)

### What You Launched
An AI system that automatically handles customer inquiries — answering questions, resolving issues, and escalating only when necessary.

### Architecture Diagram (Mental Model)

```
Customer contacts support (phone/chat/email)
         │
         ▼
┌─────────────────────────────────────┐
│     Amazon Connect (Omnichannel)     │
│  • Receives call/chat/email          │
│  • Identifies customer (phone/email)  │
│  • Passes to AI Agent                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Amazon Bedrock Agent             │
│  • Understands customer's intent      │
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

1. **Customer contacts support** via phone, chat, or email
2. **Amazon Connect** receives the contact, identifies the customer using phone number or email match against Customer Profiles
3. **Intent detection:** Connect's conversational AI (powered by Lex + Bedrock) determines what the customer wants:
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
| Amazon Connect Customer Profiles | Customer identity | Unifies customer data from CRM + contact history |

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

> "We built an AI-powered support system on Amazon Connect with Bedrock Agents. The architecture uses RAG for knowledge grounding — customer policies, SOPs, and historical case resolutions are chunked and stored in a vector database. When a customer contacts us, the AI Agent reasons through their request, retrieves relevant context from the knowledge base, and can take actions like checking shipment status or updating delivery times through API integrations. We saw X% of inquiries resolved without human intervention, reducing average handle time by Y%."

---

## 2. Case Categorization (→ RAG + LLM Classification)

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
  "issue": "Customer reported delayed pickup for order #12345",
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
  "summary": "Enterprise customer ABC Corp experiencing recurring delays at Nashville hub. 3 contacts over 5 days. Root cause: capacity planning gap for volume surge. Resolution: dedicated lane allocated starting 7/28.",
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
  "recommended_actions": ["Investigate Nashville capacity", "Proactive outreach to top 5 affected customers"]
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
- For healthcare (the enterprise context): PHI detection + HIPAA-safe storage

### Interview Walkthrough

> "We automated post-contact summarization using Amazon Bedrock. After every interaction — voice or chat — the transcript feeds into a summarization pipeline that produces structured JSON output: issue, actions taken, resolution, sentiment, and next steps. We enforce structured output through system prompts and validate against a schema. The summaries reduce after-contact work for agents by 60-70% and give supervisors instant visibility into what's happening without reading full transcripts. We also aggregate these into shift-level and weekly operational summaries that surface trends and anomalies automatically."

---

## 4. TMS Automation via AI Agents (→ Bedrock Agents + Action Groups)

### What You Launched
AI Agents that autonomously interact with external Transportation Management Systems — checking status, updating records, triggering workflows.

### Architecture

```
User/System Trigger
│
├── Customer asks "reschedule my pickup"
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

**User request:** "Reschedule tomorrow's pickup for customer ABC Corp to Thursday instead"

**Agent reasoning (ReAct loop):**

```
THOUGHT: I need to find ABC Corp's scheduled pickups for tomorrow.
ACTION: check_shipment_status(customer="ABC Corp", date="2024-07-26")
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

THOUGHT: All 3 pickups rescheduled. I should notify the customer.
ACTION: send_notification(customer="ABC Corp", type="schedule_change", details=...)
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

### Healthcare Parallel (the enterprise a healthcare platform (sample))

```
Member asks: "Refill my blood pressure medication"

THOUGHT: I need to verify the member and check their prescription.
ACTION: get_member_profile(member_id="MBR-12345")
OBSERVATION: Member verified. Has Rx #567 for Lisinopril 10mg, last filled 6/25.

THOUGHT: Rx is eligible for refill (30-day supply, 25 days elapsed). Check pharmacy availability.
ACTION: check_pharmacy_inventory(pharmacy="the enterprise #4521", ndc="12345-678-90")
OBSERVATION: In stock. Ready for pickup in 2 hours.

THOUGHT: All clear. Process the refill.
ACTION: submit_refill(rx_id="567", pharmacy="the enterprise #4521", pickup_date="today")
OBSERVATION: Refill submitted. Ready by 4:00 PM.

ACTION: send_notification(member="MBR-12345", type="refill_ready", details=...)

FINAL RESPONSE: "Your Lisinopril 10mg refill has been submitted! 
It'll be ready for pickup at the enterprise #4521 by 4:00 PM today. 
Need anything else?"
```

### Interview Walkthrough

> "We built AI Agents using Amazon Bedrock that can autonomously interact with our TMS and other external systems. The architecture uses the ReAct pattern — the agent reasons about what it needs to do, calls the appropriate tools (Lambda functions that wrap our TMS APIs), observes the results, and continues until the task is complete. Key design decisions: we defined clear tool schemas using OpenAPI specs, implemented guardrails so write operations require confirmation, and built rollback capability for every automated action. This pattern handles multi-step workflows that previously required operators to navigate 3-4 different systems manually."

---

## 5. MCP Servers for BI Insights (→ Natural Language to SQL/API)

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

## Quick Reference: End-to-End Architecture for a healthcare platform (sample)

If asked "How would you architect an AI-native health platform?":

```
┌──────────────────────────────────────────────────────────┐
│                    AI-NATIVE PLATFORM (REFERENCE)                      │
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
- [ ] Can translate each solution to a Healthcare/the enterprise use case
- [ ] Know the GCP equivalents (Vertex AI, Gemini, BigQuery, GKE)
- [ ] Can discuss guardrails, especially for healthcare (HIPAA, PHI)
- [ ] Have 2-3 metrics for each solution's impact
- [ ] Can explain failure modes and how you handle them


---

# PART 2: PRACTICAL PREPARATION PROGRAM

> This is your hands-on curriculum to build real, demonstrable skills — not just talk about them. Each section has learning content PLUS working labs you can execute. The goal: walk into any interview able to whiteboard architecture, discuss real trade-offs, and prove you've actually built things.

---

## People Management Preparation

The the enterprise role is fundamentally a people leadership role: *"Lead, mentor, and grow engineering managers and senior engineers, owning hiring, performance management, career development, succession planning."* You manage managers — this is second-line leadership.

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
- **Situation:** At a logistics platform, I inherited managers of varying experience — some first-time managers promoted from strong ICs.
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

**Q: "How would you architect the AI infrastructure for a healthcare platform (sample) to scale to millions of members?"**

> "I'd design in layers. At the base, a model gateway that abstracts the LLM provider (Vertex AI/Gemini) with built-in rate limiting, semantic caching, and cost tracking. Above that, a RAG layer with a managed vector store for member context and clinical knowledge. Then an agent orchestration layer for multi-step workflows. Critically, an evaluation/observability layer from day one — we need to catch AI errors before members do. And wrapping everything, a governance layer with PHI guardrails and audit logging for HIPAA. For scale, async processing for non-realtime tasks, streaming for chat UX, and aggressive semantic caching since many member questions repeat."

**Q: "How do you control AI costs at scale?"**

> "Four levers: First, semantic caching — many queries are similar, so cache embeddings and responses. Second, model routing — use small/cheap models for simple classification, reserve powerful models for complex reasoning. Third, prompt optimization — every token costs money, so tight prompts matter at scale. Fourth, per-team cost attribution so teams own their spend. I'd set up dashboards tracking cost-per-interaction and alert on anomalies."

---

## AI-Assisted Coding Preparation

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

### How to Use the Labs

The labs live in `the `labs/` folder in this repo`. Each lab has:
- A `README.md` with learning objectives and step-by-step instructions
- Starter code with `TODO` markers
- A working reference solution
- "Interview talking points" — what you learned to say

Ask me to walk you through any lab, or say "start Lab 1" and I'll guide you interactively.

### Lab 1: Build a RAG System (Week 1)

**What you'll build:** A working retrieval-augmented Q&A system over a set of documents.

**You'll learn:**
- How embeddings turn text into vectors
- How vector similarity search works
- How RAG grounds LLM responses in your data
- Why chunking strategy matters

**Concepts demonstrated:** Embeddings, vector stores, semantic search, prompt construction, grounding

### Lab 2: Build an AI Agent (Week 2)

**What you'll build:** An agent that answers questions AND takes actions using tools.

**You'll learn:**
- The ReAct pattern (Reason + Act)
- How to define and register tools
- How agents decide which tool to call
- Guardrails and error handling

**Concepts demonstrated:** Agentic AI, tool-use/function calling, multi-step reasoning

### Lab 3: Ship a Feature with AI-Assisted Coding (Week 3)

**What you'll build:** A small full-stack feature using AI coding tools end-to-end.

**You'll learn:**
- Spec-driven development workflow
- How to prompt effectively for code
- How to review and validate AI-generated code
- The quality gates that matter

**Concepts demonstrated:** Modern AI dev workflow, code review discipline, testing

### Lab 4: AI Infrastructure — Deploy & Observe (Week 4)

**What you'll build:** Deploy a model endpoint with monitoring, caching, and cost tracking.

**You'll learn:**
- Model serving patterns
- Semantic caching for cost reduction
- Observability and evaluation
- Scaling considerations

**Concepts demonstrated:** MLOps/LLMOps, cost optimization, production readiness

### Lab 5: Popular Frameworks & Patterns (HuggingFace, LangChain, LlamaIndex)

**What you'll build:** Run real HuggingFace models locally + explore LangChain patterns.

**You'll learn:**
- The framework ecosystem and when to use each
- Running open models yourself (critical for PHI/HIPAA)
- Zero-shot classification (categorize WITHOUT training data)
- LangChain patterns: chains, RAG, agents, memory
- Build-vs-buy-vs-framework leadership judgment

**Concepts demonstrated:** HuggingFace transformers, LangChain, LlamaIndex, framework trade-offs

**Runnable examples (real models, no API key):**
- Sentiment analysis → member/customer satisfaction routing
- Zero-shot classification → case categorization with no training data
- Summarization → AI post-contact summaries
- NER → PII/PHI detection for HIPAA redaction

**Interview power line:** *"I self-host open models via HuggingFace when data can't leave our boundary — critical for PHI. I use LangChain/LlamaIndex to accelerate standard RAG and agent patterns, but drop to the raw cloud SDK for high-scale production paths. The judgment is always: does the framework earn its place without hiding what matters?"*

---

