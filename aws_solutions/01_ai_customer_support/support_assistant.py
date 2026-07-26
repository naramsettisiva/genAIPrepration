#!/usr/bin/env python3
"""
Solution 1: AI-Powered Customer Support (AWS Bedrock)
=====================================================
A support assistant that answers customer questions grounded in your knowledge
base (RAG) and can invoke tools. This script demonstrates the core Bedrock calls
you'd wire into Amazon Connect or a chat widget.

Two modes:
  A) retrieve_and_generate  — managed RAG using a Bedrock Knowledge Base
  B) direct_converse        — direct model call with your own context

Prereqs: AWS creds configured, Bedrock model access granted (Claude 3 Sonnet).
Run: python3 support_assistant.py
"""

import boto3
import json

REGION = "us-east-1"
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
# Set this after you create a Knowledge Base in the Bedrock console (Solution 1 README)
KNOWLEDGE_BASE_ID = None  # e.g. "ABCD1234EF"


def direct_converse(question: str, context: str) -> str:
    """
    Mode B: Direct call to Claude via the Bedrock Converse API with your own
    retrieved context. Use when you manage retrieval yourself.
    """
    client = boto3.client("bedrock-runtime", region_name=REGION)
    system = [{
        "text": ("You are a helpful customer support assistant. Answer using ONLY "
                 "the provided context. If the answer isn't in the context, say you "
                 "don't have that information and offer to connect a human agent.")
    }]
    messages = [{
        "role": "user",
        "content": [{"text": f"Context:\n{context}\n\nQuestion: {question}"}]
    }]
    resp = client.converse(
        modelId=MODEL_ID,
        system=system,
        messages=messages,
        inferenceConfig={"maxTokens": 500, "temperature": 0.2},
    )
    return resp["output"]["message"]["content"][0]["text"]


def retrieve_and_generate(question: str, kb_id: str) -> str:
    """
    Mode A: Fully-managed RAG. Bedrock retrieves from your Knowledge Base and
    generates a grounded answer in one call. This is the production path.
    """
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)
    resp = client.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": f"arn:aws:bedrock:{REGION}::foundation-model/{MODEL_ID}",
            },
        },
    )
    answer = resp["output"]["text"]
    citations = resp.get("citations", [])
    return answer, citations


def main():
    print("=" * 68)
    print("Solution 1: AI-Powered Customer Support (Bedrock)")
    print("=" * 68)

    # Sample context (in production this comes from your Knowledge Base / RAG)
    sample_context = (
        "Specialist Visit: $50 copay, referral required. "
        "Prescription refills: use the mobile app or call the pharmacy; "
        "eligible when 25% or less of the medication remains."
    )
    question = "What is the copay for a specialist and do I need a referral?"

    if KNOWLEDGE_BASE_ID:
        print("\n[Mode A] Managed RAG via Knowledge Base:")
        answer, citations = retrieve_and_generate(question, KNOWLEDGE_BASE_ID)
        print(f"  Q: {question}\n  A: {answer}")
        print(f"  Citations: {len(citations)} source(s)")
    else:
        print("\n[Mode B] Direct Converse with provided context")
        print("  (Set KNOWLEDGE_BASE_ID to use managed RAG — see README)\n")
        answer = direct_converse(question, sample_context)
        print(f"  Q: {question}\n  A: {answer}")


def lambda_handler(event, context):
    """
    API Gateway handler. Expects JSON body: {"question": "...", "context": "..."}
    Uses managed RAG if KNOWLEDGE_BASE_ID env var is set, else direct Converse.
    """
    import os
    body = json.loads(event.get("body") or "{}")
    question = body.get("question", "")
    kb_id = os.environ.get("KNOWLEDGE_BASE_ID") or KNOWLEDGE_BASE_ID
    try:
        if kb_id:
            answer, citations = retrieve_and_generate(question, kb_id)
            result = {"answer": answer, "sources": len(citations)}
        else:
            ctx = body.get("context", "")
            result = {"answer": direct_converse(question, ctx)}
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    main()
