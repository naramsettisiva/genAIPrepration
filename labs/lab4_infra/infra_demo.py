#!/usr/bin/env python3
"""
Lab 4: AI Infrastructure — Gateway with Caching, Routing & Cost Tracking
========================================================================
Simulates a production AI gateway demonstrating the key cost/reliability
levers every AI leader must understand:
  1. Semantic caching  (similar queries hit cache -> huge savings)
  2. Model routing      (cheap model for simple, powerful for complex)
  3. Cost tracking      (per-request cost attribution)
  4. Observability      (latency, cache-hit-rate)

Uses local embeddings for semantic similarity (no API key needed).

Run: python3 infra_demo.py
"""

import time
import numpy as np

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
CACHE_SIMILARITY_THRESHOLD = 0.85   # how similar to count as a cache hit
COST_PER_1K_TOKENS = {
    "cheap":    0.00025,   # e.g., Nova Micro / Gemini Flash
    "powerful": 0.01500,   # e.g., Claude Sonnet / Gemini Pro
}


class AIGateway:
    def __init__(self, embedder):
        self.embedder = embedder
        self.cache = []          # list of (query_vec, query_text, response)
        self.total_cost = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        self.metrics = []

    # -- Semantic cache -----------------------------------------------------
    def _check_cache(self, query_vec):
        for cached_vec, cached_q, cached_resp in self.cache:
            sim = self._cosine(query_vec, cached_vec)
            if sim >= CACHE_SIMILARITY_THRESHOLD:
                return cached_resp, cached_q, sim
        return None, None, None

    @staticmethod
    def _cosine(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

    # -- Model routing ------------------------------------------------------
    def _route_model(self, query):
        """Simple heuristic: short/factual -> cheap, complex -> powerful.
        In production an LLM or classifier makes this decision."""
        complex_signals = ["explain", "why", "compare", "analyze", "recommend",
                           "should i", "what if", "diagnose"]
        if any(sig in query.lower() for sig in complex_signals):
            return "powerful"
        return "cheap"

    def _invoke_model(self, model, query):
        # Simulate model latency + token usage
        tokens = len(query.split()) * 20  # fake token count
        latency = 0.05 if model == "cheap" else 0.4
        time.sleep(latency)
        cost = (tokens / 1000) * COST_PER_1K_TOKENS[model]
        response = f"[{model} model response to: '{query[:40]}...']"
        return response, cost, latency, tokens

    # -- Main request handler ----------------------------------------------
    def handle(self, query):
        start = time.time()
        query_vec = self.embedder.encode([query], convert_to_numpy=True)[0]

        # 1. Try cache
        cached, matched_q, sim = self._check_cache(query_vec)
        if cached:
            self.cache_hits += 1
            elapsed = time.time() - start
            self.metrics.append({"query": query, "cache": "HIT", "cost": 0.0,
                                 "latency": elapsed})
            print(f"  ✅ CACHE HIT (similarity {sim:.2f} to '{matched_q[:35]}...')")
            print(f"     Cost: $0.00 | Latency: {elapsed*1000:.0f}ms | Response served from cache")
            return cached

        # 2. Cache miss -> route to a model
        self.cache_misses += 1
        model = self._route_model(query)
        response, cost, latency, tokens = self._invoke_model(model, query)
        self.total_cost += cost
        self.cache.append((query_vec, query, response))

        elapsed = time.time() - start
        self.metrics.append({"query": query, "cache": "MISS", "model": model,
                             "cost": cost, "latency": elapsed})
        print(f"  ❌ CACHE MISS -> routed to '{model}' model")
        print(f"     Cost: ${cost:.5f} | Latency: {elapsed*1000:.0f}ms | Tokens: {tokens}")
        return response

    def dashboard(self):
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total else 0
        # Estimate cost WITHOUT caching (every request would have hit a model)
        avg_cost_per_miss = (self.total_cost / self.cache_misses) if self.cache_misses else 0
        cost_without_cache = avg_cost_per_miss * total
        savings = cost_without_cache - self.total_cost

        print("\n" + "=" * 70)
        print("AI GATEWAY OBSERVABILITY DASHBOARD")
        print("=" * 70)
        print(f"  Total requests:      {total}")
        print(f"  Cache hits:          {self.cache_hits} ({hit_rate:.0f}%)")
        print(f"  Cache misses:        {self.cache_misses}")
        print(f"  Actual cost:         ${self.total_cost:.5f}")
        print(f"  Cost without cache:  ${cost_without_cache:.5f}")
        print(f"  💰 Savings from cache: ${savings:.5f} ({(savings/cost_without_cache*100) if cost_without_cache else 0:.0f}%)")
        print("\n  --- Projected at 1,000,000 requests/day ---")
        if total:
            scale = 1_000_000 / total
            print(f"  Cost with caching:    ${self.total_cost * scale:,.2f}/day")
            print(f"  Cost without caching: ${cost_without_cache * scale:,.2f}/day")
            print(f"  Daily savings:        ${savings * scale:,.2f}/day")
            print(f"  Annual savings:       ${savings * scale * 365:,.2f}/year")


def main():
    print("\n" + "#" * 70)
    print("# LAB 4: AI INFRASTRUCTURE GATEWAY")
    print("#" * 70)

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("\nRun: pip install -r requirements.txt\n")
        return
    print("\nLoading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    gateway = AIGateway(embedder)

    # Simulated traffic — note the similar queries that should hit cache
    queries = [
        "What is the copay for a specialist?",       # miss - cheap
        "How much do I pay to see a specialist?",    # HIT (similar to above)
        "What's the specialist visit cost?",          # HIT (similar)
        "Explain why my claim was denied",            # miss - powerful (complex)
        "Why was my claim denied?",                   # HIT (similar to above)
        "How do I refill my prescription?",           # miss - cheap
        "What are the steps to refill a medication?", # HIT (similar)
        "Compare the Gold and Silver plans for me",   # miss - powerful (complex)
    ]

    print(f"\nProcessing {len(queries)} queries through the gateway...\n")
    for i, q in enumerate(queries, 1):
        print(f"[Request {i}] \"{q}\"")
        gateway.handle(q)
        print()

    gateway.dashboard()
    print("\nYou just ran an AI gateway with caching, routing & cost tracking!\n")


if __name__ == "__main__":
    main()
