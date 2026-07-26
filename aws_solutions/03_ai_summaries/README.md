# Solution 3: AI Summaries with PII Redaction

Generate structured post-contact summaries from transcripts, with automatic PII/PHI
detection and redaction — critical for HIPAA/regulated industries.

## Architecture

```
Transcript (voice/chat)
   │
   ▼
Lambda ──► Amazon Comprehend (detect_pii_entities -> redact)
       ──► Amazon Bedrock / Claude (structured JSON summary)
       ──► validated output {issue, actions_taken, resolution, sentiment, follow_up}
       ──► store in DynamoDB / case record
```

## AWS Services
- **Amazon Comprehend** — `detect_pii_entities` finds names, emails, SSNs, phone numbers
- **Amazon Bedrock — Claude 3 Sonnet** — structured summarization with enforced JSON schema
- **Lambda** — orchestration
- **DynamoDB / S3** (optional) — persist summaries

## Key Design Points
- **PII redaction BEFORE the LLM** — sensitive data never reaches the model (compliance)
- **Structured output** — system prompt enforces a strict JSON schema for downstream use
- **Grounded** — instructed to summarize only from the transcript (no hallucination)

## Deploy / Run

### Local test (needs AWS creds + Bedrock + Comprehend access)
```bash
cd aws_solutions/03_ai_summaries
pip install -r requirements.txt
python3 summarize.py
```

### As a Lambda
Deploy `summarize.py` (has a `lambda_handler`) behind API Gateway or trigger from your
contact-center pipeline. IAM permissions needed:
```
bedrock:Converse, bedrock:InvokeModel
comprehend:DetectPiiEntities
```

## HIPAA / Healthcare Notes
- Comprehend Medical (`comprehend-medical`) can additionally detect PHI (diagnoses, meds)
- Ensure all services are used under a **BAA** and encrypt data at rest/in transit
- For clinical content, add human review before the summary enters a patient record

## Interview Talking Point
> "I built structured post-contact summarization on Bedrock. The key design decision is
> redacting PII with Comprehend BEFORE the transcript reaches the LLM — so sensitive data
> never leaves the compliance boundary. Claude produces a strict JSON schema (issue,
> actions, resolution, sentiment, follow-up) enforced via the system prompt, which makes
> the output reliable for downstream systems. For healthcare I'd use Comprehend Medical for
> PHI detection and add human review for anything clinical."
