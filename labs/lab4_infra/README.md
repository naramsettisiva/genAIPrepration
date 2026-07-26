# Lab 4: AI Infrastructure — Caching, Cost & Observability

## Learning Objectives
- Understand **semantic caching** and why it's a top cost-reduction lever
- Learn **model routing** (cheap vs. powerful models)
- See **observability** for AI systems (latency, cost, quality tracking)
- Understand production **scaling patterns**

## The Big Picture

At scale, AI infrastructure is about three things: **cost, reliability, and observability.** A naive AI system can cost 10x more than an optimized one. Leaders must understand these levers.

## How To Run

```bash
cd genAIPrepration/labs/lab4_infra
pip install -r requirements.txt
python3 infra_demo.py
```

The demo simulates an AI gateway with:
1. **Semantic caching** — similar questions hit the cache (huge savings)
2. **Model routing** — simple queries → cheap model, complex → powerful
3. **Cost tracking** — see the running cost per request
4. **Observability** — latency and cache-hit metrics

## What You'll See

The demo sends several queries, some similar. Watch:
- First query: cache MISS, calls "expensive" model, costs $
- Similar query: cache HIT, near-zero cost, instant
- Cost dashboard showing total spend and savings from caching

## Learning Exercises

1. **Run it** — observe cache hits vs. misses and cost impact
2. **Tune the cache threshold** — how similar must queries be to hit cache?
3. **Add a model tier** — add a "medium" model for medium-complexity queries
4. **Calculate savings** — at 1M queries/day, what does caching save?

## Key Infrastructure Concepts

**Semantic caching:** Instead of exact-match caching, embed the query and check if a *similar* query was already answered. Massive savings when users ask variations of the same thing.

**Model routing:** Not every query needs the most powerful (expensive) model. Route simple classification to a cheap model, complex reasoning to a powerful one. Can cut costs 60-80%.

**Cost tracking:** At scale, per-team/per-use-case cost attribution is essential. You can't manage what you don't measure.

**Scaling patterns:**
- Async processing (queues) for non-realtime
- Streaming responses for chat UX
- Provisioned throughput for predictable load, on-demand for spikes

## Interview Talking Points

> "AI cost governance is a real engineering discipline. I built a gateway pattern demonstrating the key levers: semantic caching, where similar queries hit a cache instead of re-invoking the model — at scale this can save 40%+; model routing, where simple queries go to cheap models and only complex reasoning uses expensive ones; and per-request cost tracking for accountability. For an AI-native platform like HealthConnect (sample) serving millions of members, these aren't optional — the difference between naive and optimized infrastructure can be 10x on cost. I'd also insist on observability from day one: latency, cost, cache-hit-rate, and answer-quality metrics, plus evaluation pipelines to catch model drift."

## Production Mapping

| Concept | AWS | GCP |
|---------|-----|-----|
| Model gateway | Bedrock + API Gateway | Vertex AI + Apigee |
| Semantic cache | ElastiCache + embeddings | Memorystore + embeddings |
| Model routing | Bedrock (multi-model) | Vertex AI Model Garden |
| Observability | CloudWatch + Bedrock metrics | Cloud Monitoring + Vertex |
| Evaluation | Bedrock Model Evaluation | Vertex AI Evaluation |
