# Lab 1: Build a RAG System

## Learning Objectives
By the end of this lab, you'll understand — and be able to explain in an interview:
- How **embeddings** convert text into numerical vectors
- How **vector similarity search** finds relevant information
- How **RAG (Retrieval-Augmented Generation)** grounds LLM answers in your data
- Why **chunking strategy** matters
- The full RAG pipeline end-to-end

## The Big Picture

RAG solves a core LLM problem: LLMs don't know YOUR data and can hallucinate. RAG fixes this by:
1. Storing your documents as searchable vectors
2. Finding the most relevant chunks for a question
3. Giving those chunks to the LLM as context
4. The LLM answers using YOUR data, not its training memory

```
Question → [Embed] → [Search vectors] → [Retrieve top chunks] → [LLM + chunks] → Grounded Answer
```

## What's In This Lab

- `rag_demo.py` — A complete, runnable RAG system (no external API needed — uses local embeddings)
- `documents/` — Sample healthcare knowledge documents to search over
- `SOLUTION_NOTES.md` — Deep explanation of each step + interview talking points

## How To Run

```bash
cd genAIPrepration/labs/lab1_rag
pip install -r requirements.txt
python3 rag_demo.py
```

Then ask questions like:
- "What is the copay for a specialist visit?"
- "How do I refill a prescription?"
- "What is the deductible?"

## Learning Exercises

1. **Run it as-is** — see RAG answer questions from the documents
2. **Add a document** — drop a new `.txt` in `documents/`, re-run, see it get indexed
3. **Break it** — ask a question NOT in the docs. See how it responds (grounding vs. hallucination)
4. **Tune chunking** — change `CHUNK_SIZE` in the code. See how it affects retrieval quality
5. **Inspect retrieval** — the code prints which chunks were retrieved. Study why those matched

## Interview Talking Points (what you'll be able to say)

> "I built a RAG system from scratch. The pipeline embeds documents into vectors using an embedding model, stores them in a vector index, and at query time embeds the question, does a cosine-similarity search to find the most relevant chunks, then passes those to the LLM as grounding context. I learned firsthand why chunking strategy matters — too large and you get noise, too small and you lose context. I also saw how RAG dramatically reduces hallucination because the model answers from retrieved facts, not memory."
