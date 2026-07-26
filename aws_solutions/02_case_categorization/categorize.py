#!/usr/bin/env python3
"""
Solution 2: Case Categorization (AWS Bedrock — RAG + LLM Classification)
=======================================================================
Classify incoming support cases by intent using few-shot retrieval + Claude.
No model training required — add new categories by just editing the list.

Pipeline:
  incoming case -> Titan embedding -> retrieve similar labeled cases
                -> Claude classifies with those examples -> confidence-based routing

Prereqs: Bedrock model access (Titan Embeddings V2 + Claude 3 Sonnet).
Run: python3 categorize.py
"""

import boto3
import json
import numpy as np

REGION = "us-east-1"
EMBED_MODEL = "amazon.titan-embed-text-v2:0"
LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"

CATEGORIES = ["shipment delay", "billing dispute", "pickup scheduling",
              "damage claim", "rate inquiry", "account issue", "other"]

# Small labeled set for few-shot retrieval (in prod: thousands, in a vector DB)
LABELED_CASES = [
    ("My invoice charged me twice for the same load", "billing dispute"),
    ("Where is my shipment, it was due yesterday", "shipment delay"),
    ("I need to move my pickup to Thursday", "pickup scheduling"),
    ("The pallet arrived crushed and goods are broken", "damage claim"),
    ("How much do you charge for a Nashville to Dallas lane", "rate inquiry"),
    ("I can't log into my account portal", "account issue"),
]

_bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def embed(text: str) -> np.ndarray:
    resp = _bedrock.invoke_model(
        modelId=EMBED_MODEL,
        body=json.dumps({"inputText": text}),
    )
    vec = json.loads(resp["body"].read())["embedding"]
    return np.array(vec, dtype=np.float32)


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def retrieve_similar(case_text, labeled_vecs, k=3):
    q = embed(case_text)
    scored = [(cosine(q, v), text, label) for v, (text, label) in labeled_vecs]
    scored.sort(reverse=True)
    return scored[:k]


def classify(case_text, examples) -> dict:
    example_block = "\n".join(
        f'- "{txt}" -> {label}' for _, txt, label in examples
    )
    prompt = (
        f"Classify the support case into exactly one category.\n"
        f"Categories: {', '.join(CATEGORIES)}\n\n"
        f"Similar labeled examples:\n{example_block}\n\n"
        f'New case: "{case_text}"\n\n'
        f'Respond as JSON: {{"category": "...", "confidence": "high|medium|low", '
        f'"reason": "..."}}'
    )
    resp = _bedrock.converse(
        modelId=LLM_MODEL,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 200, "temperature": 0.0},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    try:
        start, end = text.index("{"), text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"category": "other", "confidence": "low", "reason": text[:100]}


def categorize_case(case_text, labeled_vecs):
    examples = retrieve_similar(case_text, labeled_vecs)
    result = classify(case_text, examples)
    # Confidence-based routing
    if result["confidence"] == "high":
        result["routing"] = f"auto-route to '{result['category']}' queue"
    elif result["confidence"] == "medium":
        result["routing"] = "auto-route + flag for QA review"
    else:
        result["routing"] = "send to human triage"
    return result


def main():
    print("=" * 68)
    print("Solution 2: Case Categorization (Bedrock RAG + Claude)")
    print("=" * 68)
    print("\nEmbedding labeled cases (Titan)...")
    labeled_vecs = [(embed(t), (t, l)) for t, l in LABELED_CASES]

    new_cases = [
        "You billed me for a shipment I never booked",
        "My freight is 2 days late and customer is angry",
    ]
    for c in new_cases:
        print(f"\nCase: '{c}'")
        r = categorize_case(c, labeled_vecs)
        print(f"  -> {r['category']} (confidence: {r['confidence']})")
        print(f"     routing: {r['routing']}")
        print(f"     reason: {r.get('reason','')[:80]}")


if __name__ == "__main__":
    main()
