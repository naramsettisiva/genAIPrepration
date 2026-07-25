# Hands-On GenAI Labs

A practical, runnable curriculum for building real GenAI engineering skills — from RAG
and agents to AI infrastructure and popular frameworks. Each lab is self-contained,
runs locally (no API key required for the core demos), and includes learning notes.

## The Labs

| Lab | Topic | Runnable | Time |
|-----|-------|----------|------|
| [Lab 1](lab1_rag/README.md) | RAG System from scratch | ✅ | 1-2 hrs |
| [Lab 2](lab2_agent/README.md) | AI Agent (ReAct + tools) | ✅ | 1-2 hrs |
| [Lab 3](lab3_ai_coding/README.md) | Ship a feature with AI-assisted coding | Guided | 1-2 hrs |
| [Lab 4](lab4_infra/README.md) | AI Infrastructure (caching, routing, cost) | ✅ | 1-2 hrs |
| [Lab 5](lab5_frameworks/README.md) | Frameworks: HuggingFace, LangChain, LlamaIndex | ✅ | 1-2 hrs |

## Quick Start

```bash
# Lab 1: RAG from scratch
cd lab1_rag && pip install -r requirements.txt && python3 rag_demo.py

# Lab 2: AI Agent with tools (ReAct pattern)
cd ../lab2_agent && python3 agent_demo.py

# Lab 4: AI gateway (semantic caching, model routing, cost tracking)
cd ../lab4_infra && pip install -r requirements.txt && python3 infra_demo.py

# Lab 5: Real HuggingFace models + LangChain patterns
cd ../lab5_frameworks && pip install -r requirements.txt && python3 hf_demo.py
python3 langchain_patterns.py
```

## What You'll Learn

- **RAG** — embeddings, vector search, chunking strategy, grounding to reduce hallucination
- **Agents** — the ReAct pattern (Reason + Act), tool-use / function calling, guardrails
- **AI-assisted coding** — spec-driven development, prompting, reviewing AI-generated code
- **AI infrastructure** — semantic caching, model routing, cost governance, observability
- **Frameworks** — HuggingFace (self-hosted models), LangChain, LlamaIndex, and when to use each

## Design Principles

- **Runnable over theoretical** — you execute real code and see real output
- **Cloud-agnostic** — patterns map to both AWS (Bedrock) and GCP (Vertex AI)
- **Production-minded** — guardrails, cost, observability, and compliance are first-class
- **Sample data only** — all examples use synthetic/sample data

## Requirements

- Python 3.9+
- See each lab's `requirements.txt` (mostly `sentence-transformers`, `transformers`, `numpy`)

## License

MIT — free to use and adapt for your own learning.
