# 🎤 Mock Interview Practice on Your Phone (Claude + ChatGPT)

Practice interviews anywhere. You have both apps — **use each for what it's actually better at.**

> **Speak your answers out loud.** Typing builds the wrong muscle. The whole point is
> rehearsing what comes out of your mouth under pressure.

---

## Which app for what

| | **Claude** | **ChatGPT** |
|---|---|---|
| **Best for** | Repeat practice with persistent context; detailed written critique | Live, realistic spoken back-and-forth |
| **Killer feature** | **Projects** — upload your prep once, reuse forever | **Advanced voice** — interrupts and follows up like a real person |
| **Voice** | Dictate your answer; reply in text (playable) | Full hands-free spoken conversation |
| **Reviewing feedback** | ✅ Scroll back through written critique | Harder — voice transcripts are messier |
| **Setup cost** | 5 min once (then zero) | Re-paste context each new chat |

**Practical split:**
- **Claude** → your home base. Set up a Project once; every session has full context and you keep a written record of critiques.
- **ChatGPT** → your dress rehearsal. Use advanced voice for the realistic pressure of being interrupted and pushed.

---

## Setup A — Claude Project (do this once, ~5 min) ⭐ recommended

This is the biggest win available to you, and it's a paid-plan feature you already have.

1. In Claude, create a **new Project** called `Interview Prep`
2. Add to **Project knowledge**:
   - Your resume (PDF/DOCX)
   - The prep guide — either upload the `.md`, or paste the link:
     `https://naramsettisiva.github.io/genAIPrepration/`
   - Any job description you're targeting
3. Set the Project's **custom instructions** to:

```
You are an experienced interviewer helping me prepare for senior engineering
leadership roles (Lead Director / Senior Engineering Manager / Principal TPM).

Use the project knowledge for my background and prep material.

Always:
- Ask ONE question at a time and wait for my full answer
- Stay in character as the interviewer; probe weak spots, don't accept vague answers
- After each answer: score 1-5, name the single biggest weakness, and show a
  stronger version in 2-3 sentences
- Flag when I ramble (senior answers should land in ~90 seconds)
- Be harsher than feels comfortable — real interviewers are less generous than you
```

**Why this matters:** every new chat in that Project already knows your background. No
re-pasting. Per Anthropic's docs, paid plans also get RAG-backed project knowledge (~10x
capacity), so you can load a lot of material.

Then just open a new chat in the Project and say: *"Run a hiring manager mock interview."*

## Setup B — ChatGPT (per-chat)

No Projects equivalent, so prime each new chat with this once:

```
I'm preparing for senior engineering leadership interviews (Lead Director /
Senior Engineering Manager / Principal TPM level).

My background:
- 24+ years experience, 12+ years in people leadership
- Currently Sr. Technical Program Manager leading a 250+ person org across
  8 engineering teams and 10+ services; grew that business line $30M → $100M
  revenue and cut cost-to-serve 48%
- Previously built an AWS consulting practice from 4 → 50+ engineers in 15 months
- Senior Development Manager at Oracle (scaled a team 30 → 80)
- Co-founder/VP Technology at a fintech startup (concept → MVP in 100 days)
- 18+ months shipping production GenAI: AI agents, RAG, MCP servers, AI-powered
  support automation
- Deep AWS; ramping on GCP

Ask ONE question at a time. Wait for my full answer. Then score it 1-5 and tell
me specifically what to improve. Be harsher than feels comfortable.
```

> 💡 Or point it at the public guide: *"Read https://naramsettisiva.github.io/genAIPrepration/
> and use it as my background, then interview me."* Confirm it actually loaded the page first.

### Turning on voice
- **ChatGPT** — tap the **voice/waveform control** on the input bar for a hands-free spoken conversation
- **Claude** — tap the **microphone** to dictate your answer

*(Both apps move their UI around between releases — if an icon isn't where described, it's
near the message input.)*

---

## The 5 Practice Modes

Same prompts work in either app. In Claude, run them inside your Project.

### 1. Hiring Manager Interview — start here

```
Act as the hiring manager for a Lead Director of Software Engineering role on an
AI-native platform team. Conduct a realistic 45-minute interview.

ONE question at a time; wait for my spoken answer. Ask natural follow-ups and
probe weak spots. Cover: background, technical depth, people leadership,
AI/GenAI delivery, cross-functional influence, and first 90 days.

After each answer: score 1-5, name the biggest weakness, show a stronger version.
Stay in character. Start with your first question.
```

### 2. Technical Deep-Dive (GenAI depth)

```
Act as a senior technical interviewer. Grill me on GenAI depth for a Lead
Director role. One question at a time.

Cover: RAG (chunking, embeddings, grounding), agents (ReAct, tool use,
guardrails), evaluation (how do I know the AI works?), AI infrastructure (cost,
caching, model routing), MCP, and build-vs-buy judgment.

Push back when I'm hand-wavy. Make me define terms I use loosely. Ask "why" and
"what would you do differently." Score each answer 1-5. Start.
```

### 3. Whiteboard / Architecture (verbal design)

```
Give me a system design prompt for a senior engineering leader, then let me think
out loud. Act as the interviewer: ask clarifying questions, add constraints
mid-way, challenge my trade-offs.

Topics: an AI-native customer support platform; a RAG system over millions of
documents; an agent that safely takes actions on production systems; the AI
infrastructure layer for a platform serving millions of users.

Don't give me the answer — coach me with questions. At the end, tell me what a
strong answer would have covered that I missed. Give me one prompt now.
```

> In **Claude**, add: *"Keep a running architecture summary as an artifact I can review."*

### 4. Behavioral / STAR drilling

```
Rapid-fire behavioral interview for a senior engineering leadership role. One
question at a time, covering: scaling teams, managing underperformers,
influencing executives when I disagreed, competing priorities, a failure I owned,
developing managers, and driving change through resistance.

After each answer: say whether it followed STAR, point out if I was vague about
MY contribution vs. the team's, flag any missing measurable result, score 1-5.
Start.
```

### 5. Reverse Interview (questions YOU ask)

```
I'm the candidate. Act as a hiring manager and let me interview YOU about the
role and team. After each question I ask, tell me what it signals about me,
whether it's too generic, and what a more senior-sounding version would be.
I'll start asking now.
```

---

## Making it work on mobile

| Situation | Do this |
|-----------|---------|
| **Commuting / walking** | ChatGPT voice, hands-free — Mode 4 (behavioral) |
| **Only 10 minutes** | Mode 4: one question, one answer, one critique |
| **Want feedback to review later** | Claude in your Project — written critique persists |
| **Practicing the 2-min pitch** | *"Just listen to my 2-minute intro, then critique it. No questions yet."* |
| **Answer felt weak** | *"Let me try that again"* — redo while it's fresh |
| **Harder mode** | *"Be a skeptical interviewer unconvinced by my AWS-to-GCP transition."* |
| **Tracking progress over weeks** | Claude Project — chat history stays in one place |

### Mid-session commands
- *"Harder."* / *"Easier."*
- *"Skip to leadership questions."*
- *"Model the perfect answer for that one."*
- *"Was that too long?"* (aim ~90 seconds, not 5 minutes)
- *"Summarize my 3 weakest areas from this session."* ← **end every session with this**

---

## A realistic caveat

AI mocks are excellent for **reps, structure, and hearing your own filler words**. They are
weak at judging executive presence and they **score more generously than real interviewers**.

- Treat 4/5 from an AI as roughly 3/5 from a real hiring manager
- Explicitly ask for harsher grading
- Do at least one mock with a **real human** before the actual interview — neither app can
  replicate someone senior deciding whether to hire you

---

## Suggested cadence

| When | Session | App | Length |
|------|---------|-----|--------|
| Daily | Mode 4 behavioral, voice, commuting | ChatGPT | 10 min |
| 2-3× / week | Mode 1 full hiring manager run | Claude Project | 30-45 min |
| Weekly | Mode 3 whiteboard, verbalize a design | Claude (artifacts) | 30 min |
| Before a real interview | Mode 5 reverse + redo your 2-min pitch | ChatGPT voice | 15 min |

Keep a running list from *"Summarize my 3 weakest areas"* — in your Claude Project it
accumulates automatically, and that list is your study plan.
