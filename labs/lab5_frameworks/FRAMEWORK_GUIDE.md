# Framework Decision Guide & Interview Depth

## The Full Ecosystem (know these names)

### Model Hubs & Runtimes
- **HuggingFace** — the "GitHub of ML." 500K+ open models, `transformers` library, `pipeline()` API. Run locally or on HF Inference Endpoints. **Healthcare angle:** self-host to keep PHI in your VPC.
- **Ollama** — run open LLMs (Llama, Mistral) locally with one command. Great for dev/prototyping.

### LLM App Frameworks
- **LangChain** — composable chains, agents, memory, 700+ integrations. Most popular, biggest ecosystem.
- **LlamaIndex** — RAG-specialized: advanced indexing, retrieval, query engines. Best for document-heavy Q&A.
- **LangGraph** — LangChain's graph-based library for stateful, cyclic, multi-agent workflows.
- **Semantic Kernel** — Microsoft's orchestration SDK (C#/Python). Common in Azure shops.
- **Haystack** — production-focused NLP/RAG framework by deepset.

### Cloud-Native (managed, production)
- **Amazon Bedrock** — managed LLMs + Agents + Knowledge Bases + Guardrails (your experience)
- **Vertex AI** — Google's platform: Gemini, Vector Search, Agent Builder (HealthConnect (sample)'s stack)
- **Azure AI Foundry** — Microsoft's managed AI platform

### Vector Databases
- **Pinecone, Weaviate, Qdrant, Chroma** — dedicated vector DBs
- **pgvector** (Postgres), **OpenSearch**, **Vertex Vector Search** — vector search in existing stores

## Popular Patterns Mapped to Your Use Cases

| Pattern | Framework Example | Your Use Case |
|---------|-------------------|---------------|
| Zero-shot classification | HuggingFace `pipeline("zero-shot-classification")` | Case categorization without training data |
| Local NER for PII | HuggingFace `pipeline("ner")` | PHI/PII redaction before storage (HIPAA) |
| Sentiment routing | HuggingFace sentiment model | Route frustrated members to human agents |
| RAG chain | LangChain / LlamaIndex retriever + LLM | Member Q&A over benefits docs |
| Tool-calling agent | LangChain `create_tool_calling_agent` | TMS/pharmacy automation |
| Conversation memory | LangChain `RunnableWithMessageHistory` | Multi-turn member conversations |
| Multi-agent workflow | LangGraph | Complex care-coordination flows |

## Build vs. Buy vs. Framework — The Leadership Decision

This is what they're really testing at Director level:

**Use a framework (LangChain/LlamaIndex) when:**
- Standard patterns, need speed to market
- Team is small or ramping on AI
- Prototyping and iterating fast

**Use cloud-managed (Bedrock/Vertex) when:**
- Production scale and reliability matter
- You want managed guardrails, monitoring, compliance
- You want to minimize operational burden

**Drop to raw SDK / build custom when:**
- Performance-critical paths (frameworks add latency)
- You've outgrown the abstraction and need control
- Debugging complex behavior the framework obscures

**Self-host (HuggingFace) when:**
- Data can't leave your boundary (PHI/HIPAA) — critical for regulated industries
- Cost at scale favors owned infrastructure
- You need a specialized/fine-tuned open model

## Interview Q&A

**Q: "What frameworks would you use for HealthConnect (sample) and why?"**

> "I'd be deliberate. For member-facing Q&A grounded in benefits and clinical docs, I'd start
> with a managed RAG approach on Vertex AI, possibly using LlamaIndex for advanced retrieval.
> For anything touching PHI where data can't leave our boundary, I'd self-host open models via
> HuggingFace in our VPC — sentiment, classification, and NER for PII redaction run great
> locally. For agent workflows like refill automation, Vertex AI Agent Builder or LangGraph
> for the complex stateful cases. My principle: frameworks to accelerate, managed services for
> scale and compliance, self-hosting when data sovereignty demands it. And I'd avoid over-
> abstracting — every layer we add is a layer to debug and secure."

**Q: "LangChain or build it yourself?"**

> "Depends on maturity and scale. LangChain is excellent for getting to a working prototype
> fast and for teams ramping on AI patterns. But I've seen production teams hit its abstraction
> limits — debugging becomes hard, and the indirection adds latency. My approach: prototype
> with the framework to learn the shape of the problem, then decide whether to keep it or drop
> to the raw SDK for the hot paths. It's the same judgment as any dependency — does it earn
> its place?"

**Q: "How do you keep up with this fast-moving space?"**

> "I read the primary sources — AWS/Google AI blogs, HuggingFace releases, key papers. But more
> importantly, I keep hands-on: I build small prototypes with new tools to form real opinions,
> not just headline familiarity. And I create space for my team to experiment — a portion of
> capacity for AI R&D — because the best signal comes from engineers actually trying things."
