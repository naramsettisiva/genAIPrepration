# Solution 6: GenAI Adoption Program (Facilitator Kit)

Unlike Solutions 1-5, this is a **program**, not code — a structured kit to drive GenAI
adoption across product and engineering teams, grounded in the AWS stack the other
solutions use. Use it to run workshops that turn "AI curiosity" into shipped use cases.

## The 4-Workshop Program

### Workshop 1 — The Art of the Possible (90 min)
- **Goal:** demystify GenAI; build a shared vocabulary
- **Content:** live demos of Solutions 1-5 (run the actual code from this repo)
- **Activity:** brainstorm 10 candidate use cases on sticky notes
- **AWS tie-in:** show the Bedrock console, model access, a live `Converse` call

### Workshop 2 — Use Case Evaluation (90 min)
- **Goal:** prioritize ruthlessly
- **Framework:** score each use case on the matrix below
- **Activity:** pick the top 3, define success metrics upfront
- **Output:** a one-page brief per selected use case

### Workshop 3 — Responsible AI & Guardrails (60 min)
- **Goal:** build judgment on risk
- **Content:** hallucination, bias, PII/PHI, human-in-the-loop
- **AWS tie-in:** Bedrock Guardrails, Comprehend PII (Solution 3), IAM least privilege
- **Activity:** the "When NOT to use AI" checklist applied to your top 3

### Workshop 4 — Hands-On Prototyping (120 min)
- **Goal:** ship a working prototype
- **Content:** prompt engineering, using the repo's labs as starting points
- **Activity:** teams build on a lab/solution and demo to stakeholders
- **AWS tie-in:** deploy a `Converse` Lambda; iterate on prompts

## Use Case Evaluation Matrix

| Criteria | Weight | Score (1-5) | How to Assess |
|----------|--------|-------------|---------------|
| Business Impact | 30% | ? | Revenue, cost, CSAT |
| Data Readiness | 25% | ? | Available, clean, sufficient? |
| Technical Feasibility | 20% | ? | Can current models handle it? |
| Risk Level | 15% | ? | Consequence if wrong? Reversible? |
| Time to Value | 10% | ? | Speed to MVP |

- **> 3.5** → prototype now
- **2.5–3.5** → investigate, close gaps
- **< 2.5** → deprioritize

## "When NOT to Use AI" Checklist

```
DON'T:
- Irreversible consequences (e.g., medication dosing)
- Regulatory requirement for human decision
- Insufficient or biased data
- Simple rules would work (over-engineering)
- Trust requires human accountability

DO:
- Repetitive + high input variability
- Speed > 100% accuracy (with human backup)
- Patterns exist in historical data
- Scale makes human review impossible
- AI augments (not replaces) human judgment
```

## Adoption Metrics to Track
- # of use cases identified / prototyped / shipped
- Team AI-tool adoption rate
- Time saved on target workflows
- Quality/accuracy of AI outputs (with human backup)
- Cost per interaction (see Lab 4 on cost governance)

## Facilitator Tips
- **Demo real code** — run this repo's solutions live; nothing builds belief like working software
- **Make it hands-on fast** — people learn by building, not slides
- **Normalize "no"** — a great outcome is deciding NOT to use AI where it doesn't fit
- **Create a standing R&D budget** — reserve team capacity for experimentation

## Interview Talking Point
> "Adoption is a leadership problem, not a tech problem. I run a 4-workshop program that
> takes teams from 'what is GenAI' to a shipped prototype, using real working demos on
> Bedrock rather than slides. The core is an Impact×Feasibility×Risk matrix so teams
> prioritize ruthlessly, plus a 'when NOT to use AI' framework — which matters most in
> regulated domains. The outcome is product teams independently bringing well-scoped AI
> opportunities instead of waiting on engineering."
