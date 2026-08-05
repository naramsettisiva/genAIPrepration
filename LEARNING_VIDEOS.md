# 🎥 Learning Videos & Courses

A curated study path that maps directly to the [labs](labs/) and
[AWS solutions](aws_solutions/) in this repo.

> **All links in this file were verified as live.** YouTube entries were validated via the
> oEmbed API (titles below are the real, returned titles). Courses/docs were checked for a
> 200 response. If a link ever rots, use the channel/search links at the bottom.

**Suggested pace:** ~1 topic per week alongside the matching lab. Watch → then build.

---

## 1. LLM Foundations
*Watch before Lab 1. Builds the mental model for everything else.*

| Video | Author | Why watch |
|-------|--------|-----------|
| [Large Language Models explained briefly](https://www.youtube.com/watch?v=LPZh9BOjkQs) | 3Blue1Brown | Best short, visual intro (~7 min) |
| [[1hr Talk] Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) | Andrej Karpathy | The single best executive-level overview |
| [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) | Andrej Karpathy | Long-form deep dive: pretraining → RLHF |
| [Transformers, the tech behind LLMs (Ch 5)](https://www.youtube.com/watch?v=wjZofJX0v4M) | 3Blue1Brown | Visual explanation of transformer architecture |
| [Attention in transformers, step-by-step (Ch 6)](https://www.youtube.com/watch?v=eMlx5fFNoYc) | 3Blue1Brown | Understand attention — the core mechanism |
| [Introduction to large language models](https://www.youtube.com/watch?v=zizonToFXDs) | Google Cloud Tech | Vendor-neutral framing; useful GCP context |
| [Let's build GPT: from scratch, in code](https://www.youtube.com/watch?v=kCc8FmEb1nY) | Andrej Karpathy | Optional/deep: code a transformer line by line |

**Interview payoff:** you can explain what an LLM actually does, why it hallucinates, and what attention means — without hand-waving.

---

## 2. RAG (Retrieval-Augmented Generation)
*Pairs with → [Lab 1: RAG](labs/lab1_rag/) and [Solution 1](aws_solutions/01_ai_customer_support/) / [Solution 2](aws_solutions/02_case_categorization/)*

| Video | Author | Why watch |
|-------|--------|-----------|
| [What is Retrieval-Augmented Generation (RAG)?](https://www.youtube.com/watch?v=T-D1OfcDW1M) | IBM Technology | Crisp ~7 min conceptual explainer |
| [Learn RAG From Scratch – Python AI Tutorial](https://www.youtube.com/watch?v=sVcwVQRHIc8) | freeCodeCamp (LangChain engineer) | Full hands-on course; mirrors Lab 1 |

**Interview payoff:** chunking trade-offs, embeddings, vector search, grounding to reduce hallucination.

---

## 3. AI Agents & Tool Use
*Pairs with → [Lab 2: Agent](labs/lab2_agent/) and [Solution 4](aws_solutions/04_tms_agent/)*

| Video | Author | Why watch |
|-------|--------|-----------|
| [What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI) | IBM Technology | Clear definition: agents vs. chatbots |
| [What's next for AI agentic workflows — Andrew Ng](https://www.youtube.com/watch?v=sal78ACtGTc) | Sequoia Capital | Strategic/leadership view of agentic AI |
| [LangChain vs LangGraph: A Tale of Two Frameworks](https://www.youtube.com/watch?v=qAF1NjEVHhY) | IBM Technology | When to use which — a real architecture decision |

**Interview payoff:** ReAct pattern, tool/function calling, when agents beat simple chains, guardrails on write actions.

---

## 4. MCP (Model Context Protocol)
*Pairs with → [Lab 6: MCP Server](labs/lab6_mcp/)*

| Video | Author | Why watch |
|-------|--------|-----------|
| [What is MCP? Integrate AI Agents with Databases & APIs](https://www.youtube.com/watch?v=eur8dUO9mvE) | IBM Technology | Short conceptual intro |
| [Why MCP really is a big deal](https://www.youtube.com/watch?v=FLpS7OfD5-s) | Confluent Developer | Why it matters architecturally (N×M problem) |
| [Building Agents with MCP — Full Workshop](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) | AI Engineer (w/ Anthropic) | Deep, practical workshop from the source |

📄 Docs: [MCP official documentation](https://modelcontextprotocol.io/docs/getting-started/intro)

**Interview payoff:** explain MCP as "USB-C for AI," describe initialize/tools-list/tools-call, and discuss auth + least privilege.

---

## 5. AWS Bedrock & AI Infrastructure
*Pairs with → all [AWS solutions](aws_solutions/) and [Lab 4: AI Infra](labs/lab4_infra/)*

| Resource | Type | Why |
|----------|------|-----|
| [Integrating Foundation Models into Your Code with Amazon Bedrock](https://www.youtube.com/watch?v=ab1mbj0acDo) | Video (AWS Developers) | Hands-on Bedrock SDK usage |
| [Generative AI Learning Plan for Developers](https://explore.skillbuilder.aws/learn/public/learning_plan/view/2068/generative-ai-learning-plan-for-developers) | AWS Skill Builder (free) | Official structured AWS path |
| [Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop) | Hands-on labs (AWS Samples) | Best practical Bedrock repo |
| [AWS Workshop Catalog](https://catalog.workshops.aws) | Workshops | Search "Bedrock", "GenAI", "Agents" |
| [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) | Docs | Authoritative reference |
| [Bedrock Agents](https://aws.amazon.com/bedrock/agents/) | Docs | Agents + Action Groups concepts |
| [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/) | Blog | Reference architectures & new features |

**Interview payoff:** name the services, explain the layers (gateway → RAG → agents → eval → governance), and talk cost levers (caching, model routing).

---

## 6. Frameworks: HuggingFace, LangChain
*Pairs with → [Lab 5: Frameworks](labs/lab5_frameworks/)*

| Resource | Type | Why |
|----------|------|-----|
| [HuggingFace LLM Course](https://huggingface.co/learn/llm-course) | Free course | Transformers, fine-tuning, running models yourself |
| [HuggingFace Agents Course](https://huggingface.co/learn/agents-course) | Free course | Build agents end-to-end |
| [HuggingFace channel](https://www.youtube.com/@HuggingFace) | YouTube | Model releases & tutorials |
| [LangChain channel](https://www.youtube.com/@LangChain) | YouTube | Patterns straight from the maintainers |

**Interview payoff:** the build-vs-buy-vs-framework judgment, and *why self-hosting matters for PHI/regulated data*.

---

## 7. Courses (structured, certificate-bearing)

| Course | Platform | Notes |
|--------|----------|-------|
| [Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms) | Coursera (AWS + DeepLearning.AI) | ⭐ Best AWS-aligned deep course |
| [DeepLearning.AI Courses](https://www.deeplearning.ai/courses) | DeepLearning.AI | Free short courses (1-2 hrs): RAG, agents, evals |
| [Generative AI catalog](https://www.coursera.org/courses?query=generative%20ai) | Coursera | Browse by depth/vendor |

---

## 8. Engineering Leadership & Interview Craft
*For the people-management and architecture-whiteboard portions of senior interviews.*

| Video | Author | Why watch |
|-------|--------|-----------|
| [Intro to Architecture and Systems Design Interviews](https://www.youtube.com/watch?v=ZgdS0EUmn70) | Jackson Gabbard (ex-Facebook) | ⭐ How senior design interviews are actually evaluated |
| [System Design Interview – Step By Step Guide](https://www.youtube.com/watch?v=bUHFg8CZFws) | System Design Interview | Repeatable framework for whiteboarding |
| [System Design Introduction For Interview](https://www.youtube.com/watch?v=UzLMhqg3_Wc) | Tushar Roy | Fundamentals refresher |

**Interview payoff:** a repeatable structure for "design an AI-native platform" prompts.

---

## Channels Worth Subscribing To

| Channel | Focus |
|---------|-------|
| [@amazonwebservices](https://www.youtube.com/@amazonwebservices) | AWS product & how-to |
| [@AWSEventsChannel](https://www.youtube.com/@AWSEventsChannel) | re:Invent / summit deep dives |
| [@anthropic-ai](https://www.youtube.com/@anthropic-ai) | Claude, MCP, agents from the source |
| [@AndrejKarpathy](https://www.youtube.com/@AndrejKarpathy) | Best-in-class LLM education |
| [@3blue1brown](https://www.youtube.com/@3blue1brown) | Visual math behind transformers |
| [@freecodecamp](https://www.youtube.com/@freecodecamp) | Long-form free courses |
| [@HuggingFace](https://www.youtube.com/@HuggingFace) | Open models |
| [@LangChain](https://www.youtube.com/@LangChain) | Framework patterns |

**Topic searches (never go stale):**
[Bedrock Knowledge Bases + RAG](https://www.youtube.com/results?search_query=amazon+bedrock+knowledge+bases+rag) ·
[Bedrock Agents on AWS Events](https://www.youtube.com/@AWSEventsChannel/search?query=bedrock%20agents)

---

## 📅 Suggested 6-Week Study Plan

| Week | Watch | Then build |
|------|-------|-----------|
| 1 | LLM Foundations (§1) | [Lab 1: RAG](labs/lab1_rag/) |
| 2 | RAG (§2) | [Solution 2: Case Categorization](aws_solutions/02_case_categorization/) |
| 3 | Agents (§3) | [Lab 2: Agent](labs/lab2_agent/) + [Solution 4](aws_solutions/04_tms_agent/) |
| 4 | Bedrock & Infra (§5) | [Lab 4: AI Infra](labs/lab4_infra/) + [Solution 1](aws_solutions/01_ai_customer_support/) |
| 5 | MCP (§4) + Frameworks (§6) | [Lab 6: MCP](labs/lab6_mcp/) + [Lab 5](labs/lab5_frameworks/) |
| 6 | Leadership & Interview Craft (§8) | Whiteboard practice + mock interviews |

**Rule of thumb:** never watch more than ~2 hours without building something. Retention comes from the build, not the video.
