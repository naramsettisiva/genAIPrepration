# Lab 5: Popular AI Frameworks & Patterns (HuggingFace, LangChain, LlamaIndex)

## Learning Objectives
- Know the **major frameworks** and when to use each (essential interview knowledge)
- Run **real HuggingFace models** locally for your use cases
- Understand **LangChain patterns** — chains, RAG, agents, memory
- Speak to **framework trade-offs** with a leader's judgment

## Why This Matters for the Interview

A Lead Director must know the ecosystem — not to code every day, but to make architecture
and build-vs-buy decisions, evaluate what teams propose, and speak credibly with engineers.

## The Framework Landscape

| Framework | What It's For | Your Use Case Fit |
|-----------|---------------|-------------------|
| **HuggingFace** | Open models you run yourself (500K+ models) | PHI-safe local inference, classification, NER, summarization |
| **LangChain** | Composable LLM app building blocks | RAG, agents, multi-step chains — rapid build |
| **LlamaIndex** | RAG-specialized framework | Document-heavy Q&A (benefits, policies) |
| **LangGraph** | Stateful, multi-agent workflows | Complex agent orchestration |
| **Bedrock/Vertex SDK** | Cloud-native, managed | Production at scale, less abstraction |

## Files In This Lab

- `hf_demo.py` — **RUNNABLE** — real HuggingFace models: sentiment, zero-shot classification, summarization, NER
- `langchain_patterns.py` — **RUNNABLE** — LangChain patterns (chains, RAG, agents, memory) with annotated real code
- `FRAMEWORK_GUIDE.md` — decision guide + interview talking points

## How To Run

```bash
cd genAIPrepration/labs/lab5_frameworks
pip install -r requirements.txt

# Real models running locally (first run downloads ~1.5GB)
python3 hf_demo.py

# LangChain patterns (runs offline with mock LLM)
python3 langchain_patterns.py
```

## HuggingFace Demo — What You'll See (all REAL models)

1. **Sentiment analysis** → detect frustrated customers/members, route to priority
2. **Zero-shot classification** → categorize cases with NO training data (just define labels!)
3. **Summarization** → auto-generate post-contact summaries
4. **NER** → extract entities / detect PII/PHI for HIPAA redaction

## LangChain Demo — Patterns Covered

1. **Chains** → `prompt | llm | parser` composable pipelines
2. **RAG chain** → retriever + prompt + LLM in ~10 lines
3. **Agents + tools** → the TMS automation pattern, framework version
4. **Memory** → multi-turn conversations

## Learning Exercises

1. **Run hf_demo.py** — see real models classify YOUR use cases
2. **Change the zero-shot labels** — add your own categories, re-run. No training needed!
3. **Test NER on PHI** — add text with names/addresses, see it detected for redaction
4. **Study langchain_patterns.py** — this is real, production-shape code
5. **Compare** — Lab 1 (raw RAG) vs LangChain RAG. When would you use each?

## Interview Talking Points

> "I know the framework ecosystem and make deliberate choices. HuggingFace is key for
> healthcare — you can run open models in your own VPC so PHI never leaves your boundary,
> and zero-shot classification lets you categorize cases without labeled training data.
> LangChain accelerates standard patterns — RAG, agents, memory — with composable blocks,
> though I'm mindful its abstraction can obscure debugging, so for high-scale production we
> sometimes drop to the raw Bedrock/Vertex SDK. LlamaIndex is my go-to when the workload is
> document-heavy retrieval. The judgment call is always: does the framework accelerate us
> without locking us in or hiding what matters?"

## Framework Decision Framework (say this if asked "which would you choose?")

```
Need to run models privately (PHI)?        -> HuggingFace (self-hosted)
Standard RAG/agent, want speed?            -> LangChain / LlamaIndex
Complex multi-agent, stateful workflows?   -> LangGraph
Max control, scale, minimal abstraction?   -> Cloud SDK (Bedrock/Vertex)
Document-centric retrieval?                -> LlamaIndex
```
