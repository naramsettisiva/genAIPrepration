# Lab 1 Solution Notes — Deep Dive

## What Just Happened (Step by Step)

### Step 1-2: Loading & Chunking
Your 3 documents became 9 chunks. **Why chunk?**
- LLMs have token limits — you can't stuff entire document sets into a prompt
- Retrieval precision — searching small chunks returns focused, relevant results
- **The trade-off:** Chunk too large → retrieval returns noise. Chunk too small → you lose context (e.g., a copay number separated from what it's for)
- **Overlap** prevents losing meaning at chunk boundaries

**Interview line:** *"Chunking strategy is a real design decision in RAG. I experimented with chunk sizes and saw that 300 characters with 50-char overlap balanced precision and context for our documents. In production you'd tune this per content type — code needs different chunking than prose."*

### Step 3: Embeddings
Each chunk became a **384-dimensional vector**. An embedding model maps text to a point in high-dimensional space where semantic meaning is preserved — "copay" and "cost" and "$50" for a doctor end up near each other.

**Interview line:** *"Embeddings are the foundation of semantic search. Unlike keyword search, embeddings capture meaning — so a question about 'doctor costs' can match a chunk about 'specialist copay' even without shared words. We used a 384-dimension model here; Bedrock Titan uses 1024 dimensions for richer representation."*

### Step 4: Vector Search (Cosine Similarity)
The question was embedded into the same vector space, then we computed **cosine similarity** against all chunk vectors. The top 3 most similar chunks were retrieved. Notice the similarity scores (0.537, 0.494, 0.480) — higher = more relevant.

**Interview line:** *"At query time, we embed the question and do a similarity search — cosine similarity measures the angle between vectors. In production, a vector database like OpenSearch, pgvector, or Pinecone does this at scale using approximate nearest-neighbor algorithms like HNSW for millisecond retrieval over millions of vectors."*

### Step 5: Generation (Grounding)
The retrieved chunks became the **context** in the prompt. The LLM is instructed to answer ONLY from that context. This is what prevents hallucination — the model isn't recalling from training memory, it's reading provided facts.

**Interview line:** *"The magic of RAG is grounding. By instructing the LLM to answer only from retrieved context, and by providing the source, we get accurate, auditable, citable answers. If the info isn't retrieved, the model says 'I don't know' rather than making something up. That auditability is essential in healthcare."*

## The Production Version

| Lab (Learning) | Production (AWS) | Production (GCP/HealthConnect (sample)) |
|---|---|---|
| Local sentence-transformers | Bedrock Titan Embeddings | Vertex AI Embeddings |
| NumPy cosine similarity | OpenSearch Serverless / pgvector | Vertex AI Vector Search |
| Simulated generation | Bedrock (Claude/Nova) | Gemini |
| In-memory vectors | Managed vector DB | Managed vector DB |
| Manual chunking | Bedrock Knowledge Bases (auto) | Vertex AI RAG Engine |

## Key Concepts You Can Now Explain

- **Embedding:** Text → vector that captures meaning
- **Vector store:** Database optimized for similarity search
- **Cosine similarity:** How we measure "closeness" of meaning
- **Chunking:** Splitting docs for precise retrieval, with overlap
- **Grounding:** Forcing the LLM to answer from retrieved facts
- **Top-K retrieval:** Getting the K most relevant chunks
- **Hallucination reduction:** RAG's core benefit

## Advanced Topics to Mention (shows depth)

- **Hybrid search:** Combine vector search with keyword (BM25) for best results
- **Re-ranking:** After retrieval, a re-ranker model re-orders chunks by relevance
- **Metadata filtering:** Filter by source, date, permissions before/after vector search
- **Chunk strategies:** Fixed-size, semantic, recursive, document-structure-aware
- **Evaluation:** Measure retrieval quality (recall@k) and answer quality (faithfulness, relevance)
