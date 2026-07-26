# GenAI Preparation

A hands-on, runnable curriculum and reference guide for building production Generative AI
systems — RAG, agents, AI infrastructure, and the modern framework ecosystem.

Everything here runs locally (no API key needed for the core demos) and maps to both
**AWS (Amazon Bedrock)** and **GCP (Vertex AI)**.

## What's Inside

### 📘 [GenAI Solutions Guide](GENAI_SOLUTIONS_GUIDE.md)

Also available as a styled, navigable **[HTML version](index.html)** — open `index.html` in
any browser, or enable GitHub Pages to view it online.
Reference architectures for six common GenAI solution patterns — AI-powered support,
case categorization, AI summaries, agentic automation, natural-language BI, and adoption
programs — plus practical sections on **people/engineering leadership, AI infrastructure,
AI-assisted coding, and popular frameworks.**

### 🚀 [AWS Deployable Solutions](aws_solutions/)
Complete, deployable reference implementations for all six GenAI use cases on the **AWS
tech stack** — working code, SAM/CloudFormation templates, and step-by-step deploy guides.

| # | Solution | AWS Services |
|---|----------|--------------|
| 1 | [AI Customer Support](aws_solutions/01_ai_customer_support/) | Bedrock Agents, Knowledge Bases, Lambda, Connect |
| 2 | [Case Categorization](aws_solutions/02_case_categorization/) | Bedrock (Titan+Claude), OpenSearch, Lambda |
| 3 | [AI Summaries](aws_solutions/03_ai_summaries/) | Bedrock, Comprehend (PII), Lambda |
| 4 | [TMS Agent](aws_solutions/04_tms_agent/) | Bedrock Agents, Action Groups, Lambda |
| 5 | [BI Insights (NL→SQL)](aws_solutions/05_bi_insights/) | Bedrock, Athena, Glue, S3 |
| 6 | [GenAI Adoption Program](aws_solutions/06_genai_adoption/) | Facilitator kit |

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
