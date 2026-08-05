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

## 7. Structured Learning Paths (hands-on)

> 💳 **Pricing validated 2026-08-05.** Ordered to match a **Coursera + Udemy subscription**.
> Free options listed after. See the pricing note on DeepLearning.AI in §7D.

### A. Coursera — covered by your subscription ⭐ start here

All hands-on with graded labs. Included with Coursera Plus.

| Path | Type | Hands-on | Why |
|------|------|----------|-----|
| [Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms) | Course (AWS + DeepLearning.AI) | AWS labs | ⭐ **Best AWS-aligned course.** Built with AWS; labs run in AWS |
| [AWS: Generative AI Applications](https://www.coursera.org/specializations/aws-generative-ai-applications) | Specialization | AWS labs | ⭐ AWS-native GenAI app building |
| [Project: GenAI Applications with RAG and LangChain](https://www.coursera.org/learn/project-generative-ai-applications-with-rag-and-langchain) | Project course | Build a real app | ⭐ Capstone-style: RAG + LangChain end-to-end |
| [Fundamentals of AI Agents using RAG and LangChain](https://www.coursera.org/learn/fundamentals-of-ai-agents-using-rag-and-langchain) | Course | Labs | Agents + RAG — maps to [Lab 1](labs/lab1_rag/) & [Lab 2](labs/lab2_agent/) |
| [Building Gen AI-Powered Applications](https://www.coursera.org/learn/building-gen-ai-powered-applications) | Course | Labs | Practical app development |
| [GenAI: LLM Architecture & Data Preparation](https://www.coursera.org/learn/generative-ai-llm-architecture-data-preparation) | Course | Labs | Foundations w/ code |
| [IBM Generative AI Engineering](https://www.coursera.org/professional-certificates/ibm-generative-ai-engineering) | Professional Certificate | Project-heavy | Deep, resume-bearing credential |
| [IBM AI Engineer](https://www.coursera.org/professional-certificates/ai-engineer) | Professional Certificate | Project-heavy | Broader ML + GenAI engineering |
| [GenAI Engineering with LLMs](https://www.coursera.org/specializations/generative-ai-engineering-with-llms) | Specialization | Labs | RAG, agents, fine-tuning |
| [ChatGPT Prompt Engineering for Developers](https://www.coursera.org/projects/chatgpt-prompt-engineering-for-developers-project) | Guided Project | Notebook | The DeepLearning.AI course, **on Coursera** |
| [Prompt Engineering](https://www.coursera.org/learn/prompt-engineering) | Course | Exercises | Practical prompt craft |
| [Generative AI for Everyone](https://www.coursera.org/learn/generative-ai-for-everyone) | Course (Andrew Ng) | Conceptual | Leadership/strategy framing |
| [Introduction to Large Language Models](https://www.coursera.org/learn/introduction-to-large-language-models) | Course (Google Cloud) | Labs | GCP-flavored fundamentals |
| [AWS Cloud Solutions Architect](https://www.coursera.org/professional-certificates/aws-cloud-solutions-architect) | Professional Certificate | AWS labs | If you want the AWS breadth credential |
| [Browse GenAI catalog](https://www.coursera.org/courses?query=generative%20ai) | — | — | Find more |

**Suggested Coursera sequence:** Generative AI with LLMs → AWS: Generative AI Applications
→ Project: GenAI Apps with RAG and LangChain.

### B. Udemy — covered by your subscription

⚠️ Udemy blocks automated link checking, so unlike every other link here I could **not**
verify specific Udemy course URLs, and individual courses get unpublished often. These
**search links** stay valid and surface current top-rated courses:

- [Amazon Bedrock](https://www.udemy.com/courses/search/?q=amazon%20bedrock)
- [LangChain](https://www.udemy.com/courses/search/?q=langchain)
- [Generative AI / LLM engineering](https://www.udemy.com/courses/search/?q=generative%20ai%20llm)
- [Model Context Protocol (MCP)](https://www.udemy.com/courses/search/?q=model%20context%20protocol)
- [AWS Certified AI Practitioner](https://www.udemy.com/courses/search/?q=aws%20certified%20ai%20practitioner)

**How to pick on Udemy:** filter for **4.5+ rating**, **updated within 6 months**, and check
the curriculum explicitly lists **hands-on projects**. GenAI courses go stale fast.

### C. Free AWS-native hands-on (no subscription needed) ⭐ highest practical value

Genuinely free — you only pay for AWS usage. This is the most *hands-on* material anywhere.

| Path | What you build | Cost |
|------|----------------|------|
| [Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop) | Real notebooks: RAG, agents, summarization, guardrails | Free (AWS usage) |
| [GenAI on AWS Workshop](https://catalog.workshops.aws/genai-on-aws/en-US) | Guided end-to-end build in your own account | Free (AWS usage) |
| [Generative AI Learning Plan for Developers](https://explore.skillbuilder.aws/learn/public/learning_plan/view/2068/generative-ai-learning-plan-for-developers) | Official AWS path w/ labs + assessments | Free |
| [AWS Workshop Catalog](https://catalog.workshops.aws) | Search "Bedrock", "Agents", "RAG" | Free |
| [AWS Skill Builder — GenAI catalog](https://explore.skillbuilder.aws/learn/external-ecommerce;view=none;redirectURL=?ctldoc-catalog-0=se-%22generative%20ai%22) | Browse all AWS GenAI training | Free tier |
| [AWS GenAI training hub](https://aws.amazon.com/training/learn-about/generative-ai/) | Role-based AWS paths | Free |
| [HuggingFace LLM Course](https://huggingface.co/learn/llm-course) | Transformers, running models yourself | Free |
| [HuggingFace Agents Course](https://huggingface.co/learn/agents-course) | Build agents end-to-end | Free |

### D. DeepLearning.AI — ⚠️ "free for a limited time" (not permanently free)

**Validated 2026-08-05:** these course pages show *"Course access is free for a limited time
during the DeepLearning.AI learning platform beta!"* with an **Enroll for Free** button. So
they are **free right now, but explicitly time-limited** — not a permanent free tier, and
**not covered by your Coursera/Udemy subscriptions** (they're on DeepLearning.AI's own
platform). Account signup required; graded assignments/certificates may need a paid membership.

**Verdict:** worth doing *now* while free, but don't build your plan around them lasting.
Most are ~1-2 hrs with hands-on notebooks:

| Course | Maps to | Duration |
|--------|---------|----------|
| [Serverless LLM Apps with Amazon Bedrock](https://www.deeplearning.ai/courses/serverless-llm-apps-amazon-bedrock) | [Solution 1](aws_solutions/01_ai_customer_support/) & [3](aws_solutions/03_ai_summaries/) | ~2h9m |
| [MCP: Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) | [Lab 6: MCP](labs/lab6_mcp/) ⭐ | ~1h58m |
| [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag) | [Lab 1: RAG](labs/lab1_rag/) | ~2h5m |
| [Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/courses/functions-tools-agents-langchain) | [Lab 2: Agent](labs/lab2_agent/) | ~1-2h |
| [AI Agents in LangGraph](https://www.deeplearning.ai/courses/ai-agents-in-langgraph) | [Lab 2](labs/lab2_agent/) & [Lab 5](labs/lab5_frameworks/) | ~1-2h |
| [Building Applications with Vector Databases](https://www.deeplearning.ai/courses/building-applications-vector-databases) | [Lab 1: RAG](labs/lab1_rag/) | ~1h |
| [LangChain: Chat with Your Data](https://www.deeplearning.ai/courses/langchain-chat-with-your-data) | [Lab 5](labs/lab5_frameworks/) | ~1h |
| [Prompt Engineering with Llama](https://www.deeplearning.ai/courses/prompt-engineering-with-llama-2) | [Lab 5](labs/lab5_frameworks/) | ~1h |
| [Browse all courses](https://www.deeplearning.ai/courses) | — | — |

### E. Other platforms

[Pluralsight paths](https://www.pluralsight.com/paths) ·
[A Cloud Guru](https://acloudguru.com) (strong AWS labs) — both separate subscriptions.

### Recommended sequence (given your Coursera + Udemy access)

1. **[Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms)** (Coursera) — AWS-built, hands-on AWS labs, the best single course for your target roles
2. **[Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop)** (free) — the most practical AWS-native hands-on repo
3. **[Project: GenAI Apps with RAG and LangChain](https://www.coursera.org/learn/project-generative-ai-applications-with-rag-and-langchain)** (Coursera) — build and ship something end-to-end
4. *Optional, while still free:* **[MCP with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic)** — best MCP course available

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

| Week | Watch | Course (hands-on) | Then build |
|------|-------|-------------------|-----------|
| 1 | LLM Foundations (§1) | 🟢 [Generative AI with LLMs](https://www.coursera.org/learn/generative-ai-with-llms) — start (Coursera) | [Lab 1: RAG](labs/lab1_rag/) |
| 2 | RAG (§2) | 🟢 [Fundamentals of AI Agents using RAG & LangChain](https://www.coursera.org/learn/fundamentals-of-ai-agents-using-rag-and-langchain) (Coursera) | [Solution 2](aws_solutions/02_case_categorization/) |
| 3 | Agents (§3) | 🟢 [Building Gen AI-Powered Applications](https://www.coursera.org/learn/building-gen-ai-powered-applications) (Coursera) | [Lab 2](labs/lab2_agent/) + [Solution 4](aws_solutions/04_tms_agent/) |
| 4 | Bedrock & Infra (§5) | 🟢 [AWS: Generative AI Applications](https://www.coursera.org/specializations/aws-generative-ai-applications) (Coursera) + [Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop) (free) | [Lab 4](labs/lab4_infra/) + [Solution 1](aws_solutions/01_ai_customer_support/) |
| 5 | MCP (§4) + Frameworks (§6) | ⚪ [MCP with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) (free *for now*) | [Lab 6](labs/lab6_mcp/) + [Lab 5](labs/lab5_frameworks/) |
| 6 | Leadership & Interview Craft (§8) | 🟢 [Project: GenAI Apps with RAG & LangChain](https://www.coursera.org/learn/project-generative-ai-applications-with-rag-and-langchain) (Coursera) | Whiteboard + mock interviews |

🟢 = covered by your Coursera subscription · ⚪ = free but time-limited (see §7D)

**Rule of thumb:** never watch more than ~2 hours without building something. Retention comes from the build, not the video.
