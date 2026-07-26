# Solution 2: Case Categorization (RAG + LLM Classification)

Auto-categorize support cases by intent — no training data required. Uses Titan
embeddings for few-shot retrieval and Claude for classification with confidence-based routing.

## Architecture

```
Incoming case (SQS/API)
   │
   ▼
Lambda ──► Titan Embeddings (embed the case)
       ──► Vector search over labeled cases (OpenSearch Serverless / in-memory)
       ──► Claude (classify using retrieved examples)
       ──► Confidence routing:
            high   -> auto-route to queue
            medium -> auto-route + QA flag
            low    -> human triage
```

## AWS Services
- **Bedrock — Titan Text Embeddings V2** — vectorize case text
- **Bedrock — Claude 3 Sonnet** — few-shot classification
- **OpenSearch Serverless** (production) — store labeled case vectors at scale
- **Lambda + SQS** — event-driven processing
- **DynamoDB** (optional) — store results + routing decisions

## Why RAG-based classification (not a trained model)?
- **No training data pipeline** — add a new category by editing a list
- **Explainable** — the model returns a reason
- **Adapts instantly** — new case types work immediately

## Deploy / Run

### Local test (needs AWS creds + Bedrock access)
```bash
cd aws_solutions/02_case_categorization
pip install -r requirements.txt
python3 categorize.py
```

### Production notes
- Replace the in-memory `LABELED_CASES` with vectors stored in **OpenSearch Serverless**
  (or a Bedrock Knowledge Base). Embed your historical labeled cases once, then query.
- Trigger the Lambda from **SQS** (decouple ingestion) or **API Gateway**.
- Persist `{case_id, category, confidence, routing}` to **DynamoDB** and emit an
  **EventBridge** event to trigger downstream routing.

## Cost
Per-case cost ≈ 1 embedding call + 1 short Claude call. Batch where possible; cache
embeddings of the labeled set (compute once, reuse).

## Interview Talking Point
> "I built RAG-based case categorization on Bedrock. Instead of training a classifier —
> which needs labeled data and retraining for new categories — I embed the incoming case
> with Titan, retrieve the most similar labeled examples via vector search, and have Claude
> classify with those as few-shot context. It returns a confidence score that drives
> routing: high-confidence auto-routes, low-confidence goes to human triage. New categories
> require zero retraining."
