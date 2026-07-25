# GenAI Preparation

A hands-on, runnable curriculum and reference guide for building production Generative AI
systems — RAG, agents, AI infrastructure, and the modern framework ecosystem.

Everything here runs locally (no API key needed for the core demos) and maps to both
**AWS (Amazon Bedrock)** and **GCP (Vertex AI)**.

## What's Inside

### 📘 [GenAI Solutions Guide](GENAI_SOLUTIONS_GUIDE.md)
Reference architectures for six common GenAI solution patterns — AI-powered support,
case categorization, AI summaries, agentic automation, natural-language BI, and adoption
programs — plus practical sections on **people/engineering leadership, AI infrastructure,
AI-assisted coding, and popular frameworks.**

### 🧪 [Hands-On Labs](labs/)
Five self-contained, runnable labs:

| Lab | Topic | Runnable |
|-----|-------|----------|
| [Lab 1](labs/lab1_rag/) | RAG system from scratch (embeddings, vector search, grounding) | ✅ |
| [Lab 2](labs/lab2_agent/) | AI agent (ReAct pattern, tool-use, guardrails) | ✅ |
| [Lab 3](labs/lab3_ai_coding/) | Ship a feature with AI-assisted coding | Guided |
| [Lab 4](labs/lab4_infra/) | AI infrastructure (semantic caching, model routing, cost) | ✅ |
| [Lab 5](labs/lab5_frameworks/) | Frameworks: HuggingFace, LangChain, LlamaIndex | ✅ |

## Quick Start

```bash
git clone https://github.com/naramsettisiva/genAIPrepration.git
cd genAIPrepration/labs/lab1_rag
pip install -r requirements.txt
python3 rag_demo.py
```

## Topics Covered

- **RAG** — embeddings, chunking strategy, vector search, grounding, hallucination reduction
- **Agents** — ReAct (Reason + Act), tool-use / function calling, orchestration, guardrails
- **AI Infrastructure** — model serving, semantic caching, model routing, cost governance, observability
- **AI-Assisted Coding** — spec-driven development, prompting, reviewing AI-generated code
- **Frameworks** — HuggingFace (self-hosted models), LangChain, LlamaIndex, LangGraph, and when to use each
- **Leadership** — building/scaling engineering orgs, responsible AI, build-vs-buy judgment

## Notes

- All examples use **synthetic/sample data**.
- Core demos run **offline** with local models; production mappings to Bedrock/Vertex are noted throughout.

## License

[MIT](LICENSE)
