# Lab 3: Ship a Feature with AI-Assisted Coding

## Learning Objectives
- Experience the **spec-driven development** workflow (how Kiro works)
- Learn to **prompt effectively** for code generation
- Practice **reviewing and validating** AI-generated code
- Understand the **quality gates** that matter when using AI tools

## The Big Picture

Modern engineering with AI assistants shifts your role:
- **Old way:** You write every line
- **New way:** You specify intent → AI generates → you review, test, integrate

Your value moves UP the stack: architecture, specification, judgment, quality.

## The Exercise: Build a "Member Copay Lookup" API

You'll build a small REST API that returns copay info by service type. Do it the modern way — spec first, then AI-assisted implementation, then validation.

### Step 1: Write the Spec (You do this)

Create `spec.md` describing what you want:
```
Feature: Copay Lookup API
- GET /copay/{service_type} returns the copay amount
- Service types: primary_care, specialist, er, urgent_care
- Returns JSON: {service_type, copay, referral_required}
- 404 if service type unknown
- Include unit tests
```

### Step 2: Generate with AI (Use me, Amazon Q, or any assistant)

Ask the AI assistant: *"Implement the feature in spec.md as a Python Flask API with unit tests."*

This is where you practice PROMPTING. Good prompts:
- Reference the spec
- Specify the tech stack
- Ask for tests
- Request error handling

### Step 3: Review the Generated Code (Critical skill!)

Don't just accept it. Check:
- [ ] Does it match the spec?
- [ ] Are edge cases handled (unknown service type)?
- [ ] Are there tests? Do they pass?
- [ ] Any security issues (input validation)?
- [ ] Does it follow good practices?

### Step 4: Validate

```bash
pip install flask pytest
python3 -m pytest test_copay.py -v
```

## Learning Exercises

1. **Write the spec yourself** — practice clear specification
2. **Generate 2 ways** — try a vague prompt vs. a detailed one. Compare quality
3. **Find a bug** — AI code often has subtle issues. Practice spotting them
4. **Add a requirement** — "now add caching" — see how AI extends existing code
5. **Reflect** — what did AI do well? Where did it need your judgment?

## Interview Talking Points

> "I practice AI-assisted development hands-on. My workflow is spec-driven — I write a clear specification, use an AI assistant to generate the implementation and tests, then I rigorously review the output. The key insight is that AI accelerates the mechanical work but the engineer's judgment is MORE important, not less — you're now reviewing and validating at a higher rate. I establish quality gates: AI-generated code goes through the same review, testing, and security scanning as any code. I've seen real productivity gains on boilerplate and test generation, but I'm vigilant about juniors maintaining fundamentals."

## Try It Now
Say **"start Lab 3"** and I'll act as your AI pair-programmer to build this feature with you, then we'll review it together.
