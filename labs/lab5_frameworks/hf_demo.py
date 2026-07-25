#!/usr/bin/env python3
"""
Lab 5a: HuggingFace Transformers — Real Models, Running Locally
================================================================
HuggingFace is the "GitHub of ML models" — 500K+ open models you can run
yourself. This is critical for healthcare where you may NOT want to send
PHI to a third-party API — you can run models in your own VPC.

This demo runs REAL models locally (no API key) for your use cases:
  1. Sentiment analysis  -> customer satisfaction
  2. Zero-shot classification -> case categorization WITHOUT training
  3. Summarization       -> AI summaries
  4. NER (entity extract) -> pull structured data / PII detection

Run: python3 hf_demo.py
"""

from transformers import pipeline

def demo_sentiment():
    print("\n" + "=" * 70)
    print("1. SENTIMENT ANALYSIS  (use case: customer satisfaction)")
    print("=" * 70)
    clf = pipeline("sentiment-analysis",
                   model="distilbert-base-uncased-finetuned-sst-2-english")
    samples = [
        "My shipment is late again and I am very frustrated!",
        "Thank you, the delivery was fast and the driver was great.",
        "I've been waiting 40 minutes to refill my prescription.",
    ]
    for s in samples:
        r = clf(s)[0]
        print(f"  '{s[:50]}...'")
        print(f"     -> {r['label']} ({r['score']:.2%})\n")
    print("  💡 In production: route NEGATIVE sentiment to priority queue / human agent")


def demo_zero_shot():
    print("\n" + "=" * 70)
    print("2. ZERO-SHOT CLASSIFICATION  (use case: case categorization)")
    print("=" * 70)
    print("  Classify WITHOUT any training data — just define labels!")
    clf = pipeline("zero-shot-classification",
                   model="facebook/bart-large-mnli")
    labels = ["shipment delay", "billing dispute", "pickup scheduling",
              "damage claim", "rate inquiry"]
    cases = [
        "The invoice charged me twice for the same load",
        "My freight arrived with a broken pallet and damaged goods",
    ]
    for case in cases:
        r = clf(case, labels)
        top = r["labels"][0]
        score = r["scores"][0]
        print(f"  Case: '{case[:55]}...'")
        print(f"     -> {top} ({score:.2%})\n")
    print("  💡 This is how you categorize cases WITHOUT labeled training data")


def demo_summarization():
    print("\n" + "=" * 70)
    print("3. SUMMARIZATION  (use case: AI post-contact summaries)")
    print("=" * 70)
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    transcript = (
        "The customer called because their scheduled pickup for order 12345 "
        "did not happen this morning. The agent investigated and found the "
        "assigned driver was reassigned due to a capacity shortage at the "
        "Nashville hub. The agent rescheduled the pickup for the next day "
        "in the morning window and applied a service credit to the account. "
        "The customer was initially frustrated but satisfied with the resolution."
    )
    r = summarizer(transcript, max_length=45, min_length=15, do_sample=False)
    print(f"  Original ({len(transcript)} chars):\n     {transcript[:80]}...\n")
    print(f"  Summary:\n     {r[0]['summary_text']}\n")
    print("  💡 Reduces after-contact work; auto-populates case notes")


def demo_ner():
    print("\n" + "=" * 70)
    print("4. NAMED ENTITY RECOGNITION  (use case: PII detection / data extract)")
    print("=" * 70)
    ner = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
    text = "Jane Doe from Memphis called about order 12345 for a logistics platform."
    entities = ner(text)
    print(f"  Text: '{text}'\n")
    for e in entities:
        print(f"     {e['entity_group']:6} -> {e['word']} ({e['score']:.2%})")
    print("\n  💡 Detect PERSON/LOCATION entities to redact PII/PHI before storage (HIPAA)")


def main():
    print("\n" + "#" * 70)
    print("# LAB 5a: HUGGINGFACE TRANSFORMERS (running real models locally)")
    print("#" * 70)
    print("\nFirst run downloads models (~1.5GB total). Subsequent runs are fast.")
    print("KEY POINT: These run in YOUR environment — critical for PHI/HIPAA.\n")

    demo_sentiment()
    demo_zero_shot()
    demo_summarization()
    demo_ner()

    print("\n" + "=" * 70)
    print("You just ran 4 production ML patterns locally with HuggingFace!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
