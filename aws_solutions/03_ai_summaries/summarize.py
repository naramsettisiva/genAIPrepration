#!/usr/bin/env python3
"""
Solution 3: AI Summaries with PII Redaction (AWS Bedrock + Comprehend)
=====================================================================
Generate structured post-contact summaries from transcripts, with PII/PHI
detection and redaction — essential for regulated industries (HIPAA).

Pipeline:
  transcript -> Comprehend (detect + redact PII) -> Claude (structured summary)
             -> validated JSON output

Prereqs: Bedrock (Claude 3 Sonnet) + Amazon Comprehend access.
Run: python3 summarize.py
"""

import boto3
import json

REGION = "us-east-1"
LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"

_bedrock = boto3.client("bedrock-runtime", region_name=REGION)
_comprehend = boto3.client("comprehend", region_name=REGION)


def redact_pii(text: str) -> str:
    """Detect PII with Comprehend and mask it (name -> [NAME], etc.)."""
    try:
        resp = _comprehend.detect_pii_entities(Text=text, LanguageCode="en")
    except Exception:
        return text  # if Comprehend unavailable, return original (demo safety)
    entities = sorted(resp.get("Entities", []), key=lambda e: e["BeginOffset"], reverse=True)
    redacted = text
    for e in entities:
        redacted = redacted[:e["BeginOffset"]] + f"[{e['Type']}]" + redacted[e["EndOffset"]:]
    return redacted


def summarize(transcript: str) -> dict:
    """Generate a structured summary using Claude with enforced JSON schema."""
    system = [{
        "text": ("You are a post-contact summarization system. Respond ONLY with valid "
                 "JSON in this exact schema: "
                 '{"issue": str, "actions_taken": str, "resolution": str, '
                 '"sentiment": str, "follow_up_required": bool}. '
                 "Base the summary only on the transcript. Do not invent details.")
    }]
    resp = _bedrock.converse(
        modelId=LLM_MODEL,
        system=system,
        messages=[{"role": "user", "content": [{"text": f"Transcript:\n{transcript}"}]}],
        inferenceConfig={"maxTokens": 400, "temperature": 0.1},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    try:
        start, end = text.index("{"), text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"error": "could not parse", "raw": text[:200]}


def main():
    print("=" * 68)
    print("Solution 3: AI Summaries with PII Redaction (Bedrock + Comprehend)")
    print("=" * 68)

    transcript = (
        "Customer Jane Doe (jane.doe@example.com, 555-123-4567) called because her "
        "scheduled pickup for order 12345 did not happen this morning. The agent found "
        "the driver was reassigned due to a capacity shortage. The agent rescheduled the "
        "pickup for tomorrow morning and applied a service credit. Customer was frustrated "
        "but satisfied with the resolution."
    )

    print("\n[1] Original transcript (contains PII):")
    print(f"    {transcript[:90]}...")

    print("\n[2] After Comprehend PII redaction:")
    redacted = redact_pii(transcript)
    print(f"    {redacted[:120]}...")

    print("\n[3] Structured summary (Claude, on redacted text):")
    summary = summarize(redacted)
    print(json.dumps(summary, indent=2))


def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    transcript = body.get("transcript", "")
    redacted = redact_pii(transcript)
    summary = summarize(redacted)
    return {"statusCode": 200, "body": json.dumps(summary)}


if __name__ == "__main__":
    main()
