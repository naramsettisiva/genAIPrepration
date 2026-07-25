#!/usr/bin/env python3
"""
Lab 1: RAG System from Scratch
================================
A complete, runnable Retrieval-Augmented Generation system.

This uses LOCAL embeddings (sentence-transformers) so you don't need any
API key to learn the concepts. In production you'd use Amazon Bedrock Titan
Embeddings or Vertex AI embeddings — but the PATTERN is identical.

Run: python3 rag_demo.py
"""

import os
import glob
import numpy as np

# ---------------------------------------------------------------------------
# CONFIGURATION — experiment with these!
# ---------------------------------------------------------------------------
CHUNK_SIZE = 300        # characters per chunk. Try 100 vs 500 to see the effect
CHUNK_OVERLAP = 50      # overlap between chunks so context isn't lost at edges
TOP_K = 3               # how many chunks to retrieve per question
DOCS_DIR = "documents"


# ---------------------------------------------------------------------------
# STEP 1: LOAD DOCUMENTS
# ---------------------------------------------------------------------------
def load_documents(docs_dir):
    """Read all .txt files from the documents directory."""
    docs = []
    for filepath in glob.glob(os.path.join(docs_dir, "*.txt")):
        with open(filepath, "r") as f:
            content = f.read()
        docs.append({"source": os.path.basename(filepath), "content": content})
    print(f"[STEP 1] Loaded {len(docs)} documents")
    return docs


# ---------------------------------------------------------------------------
# STEP 2: CHUNK DOCUMENTS
# Why chunk? LLMs have context limits, and retrieval is more precise on
# smaller pieces. Too big = noisy retrieval. Too small = lost context.
# ---------------------------------------------------------------------------
def chunk_documents(docs, chunk_size, overlap):
    chunks = []
    for doc in docs:
        text = doc["content"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({"source": doc["source"], "text": chunk_text})
            start += chunk_size - overlap
    print(f"[STEP 2] Split into {len(chunks)} chunks "
          f"(size={chunk_size}, overlap={overlap})")
    return chunks


# ---------------------------------------------------------------------------
# STEP 3: EMBED CHUNKS
# Embeddings turn text into vectors (lists of numbers). Similar meaning =
# similar vectors. This is the heart of semantic search.
# ---------------------------------------------------------------------------
def build_embedder():
    """Load a local embedding model."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("\nERROR: sentence-transformers not installed.")
        print("Run: pip install -r requirements.txt\n")
        raise
    print("[STEP 3] Loading embedding model (first run downloads ~90MB)...")
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(embedder, texts):
    """Convert a list of texts into a matrix of vectors."""
    return embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)


# ---------------------------------------------------------------------------
# STEP 4: VECTOR SEARCH (cosine similarity)
# Given a question vector, find the chunk vectors that point in the most
# similar direction. This is what a vector database does at scale.
# ---------------------------------------------------------------------------
def cosine_similarity(query_vec, doc_vecs):
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    doc_norms = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-10)
    return doc_norms @ query_norm


def retrieve(embedder, question, chunks, chunk_vecs, top_k):
    q_vec = embed_texts(embedder, [question])[0]
    scores = cosine_similarity(q_vec, chunk_vecs)
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], scores[i]) for i in top_idx]


# ---------------------------------------------------------------------------
# STEP 5: GENERATE ANSWER
# In production this calls Bedrock/Vertex/OpenAI. Here we simulate the
# "generation" step by assembling the grounded context. The KEY learning is
# how the retrieved chunks become the context that grounds the answer.
# ---------------------------------------------------------------------------
def generate_answer(question, retrieved_chunks):
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c, _ in retrieved_chunks
    )
    # This is the prompt you'd send to an LLM:
    prompt = f"""You are a helpful health plan assistant. Answer the question
using ONLY the context below. If the answer isn't in the context, say you
don't have that information.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    print("\n" + "=" * 70)
    print("RETRIEVED CONTEXT (this is what grounds the answer):")
    print("=" * 70)
    for c, score in retrieved_chunks:
        print(f"\n  [{c['source']}] (similarity: {score:.3f})")
        print(f"  {c['text'][:200]}...")

    print("\n" + "=" * 70)
    print("PROMPT SENT TO LLM (in production: Bedrock/Vertex AI):")
    print("=" * 70)
    print(prompt)
    print("\n>>> In production, the LLM would now generate a grounded answer")
    print(">>> from the context above, instead of from its training memory.")
    return prompt


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("\n" + "#" * 70)
    print("# LAB 1: RAG SYSTEM FROM SCRATCH")
    print("#" * 70 + "\n")

    docs = load_documents(DOCS_DIR)
    if not docs:
        print(f"No documents found in '{DOCS_DIR}/'. Add some .txt files!")
        return

    chunks = chunk_documents(docs, CHUNK_SIZE, CHUNK_OVERLAP)
    embedder = build_embedder()

    print("[STEP 3] Embedding all chunks into vectors...")
    chunk_texts = [c["text"] for c in chunks]
    chunk_vecs = embed_texts(embedder, chunk_texts)
    print(f"[STEP 3] Created {chunk_vecs.shape[0]} vectors "
          f"of dimension {chunk_vecs.shape[1]}")

    print("\n" + "=" * 70)
    print("RAG SYSTEM READY. Ask questions (or 'quit' to exit).")
    print("Try: 'What is the copay for a specialist?'")
    print("=" * 70)

    while True:
        try:
            question = input("\n❓ Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() in ("quit", "exit"):
            break
        retrieved = retrieve(embedder, question, chunks, chunk_vecs, TOP_K)
        generate_answer(question, retrieved)

    print("\nDone. You just ran a complete RAG pipeline!\n")


if __name__ == "__main__":
    main()
