# Solution 1: AI-Powered Customer Support

Answer customer questions grounded in your knowledge base (RAG) using Amazon Bedrock,
deployable as a serverless API and connectable to Amazon Connect.

## Architecture

```
Customer (chat/voice/API)
   │
   ▼
API Gateway ──► Lambda (support_assistant) ──► Amazon Bedrock
                                              ├─ retrieve_and_generate (managed RAG)
                                              │    └─ Bedrock Knowledge Base
                                              │         └─ OpenSearch Serverless (vectors)
                                              │              └─ S3 (source docs)
                                              └─ Converse (direct, your own context)
```

## AWS Services
- **Amazon Bedrock** — Claude 3 Sonnet for generation
- **Bedrock Knowledge Bases** — managed RAG (chunking, embeddings, retrieval)
- **OpenSearch Serverless** — vector store (auto-created by the Knowledge Base)
- **Amazon S3** — stores source documents
- **Lambda + API Gateway** — serverless endpoint
- **Amazon Connect** (optional) — invoke the Lambda from a contact flow

## Deploy

### Step 1 — Create a Knowledge Base (managed RAG)
1. Upload your documents (FAQs, policies) to an **S3 bucket**
2. Bedrock console → **Knowledge bases** → **Create knowledge base**
   - Data source: your S3 bucket
   - Embeddings model: **Titan Text Embeddings V2**
   - Vector store: **Quick create (OpenSearch Serverless)**
3. **Sync** the data source (chunks + embeds your docs)
4. Copy the **Knowledge Base ID**

### Step 2 — Deploy the API
```bash
cd aws_solutions/01_ai_customer_support
pip install -r requirements.txt

sam build
sam deploy --guided \
  --parameter-overrides KnowledgeBaseId=<YOUR_KB_ID>
```
SAM outputs an **ApiUrl**.

### Step 3 — Test
```bash
# Managed RAG (KB configured):
curl -X POST <ApiUrl> -d '{"question":"What is the specialist copay?"}'

# Direct mode (no KB):
curl -X POST <ApiUrl> -d '{"question":"What is the copay?","context":"Specialist: $50 copay"}'
```

### Local test (no deploy)
```bash
python3 support_assistant.py   # uses Converse with sample context
```

## Connect to Amazon Connect (optional)
In your Connect contact flow, add an **Invoke AWS Lambda function** block pointing to
`SupportFunction`, pass the caller's utterance as input, and speak the returned answer.

## Tear Down
```bash
sam delete
```
(Also delete the Knowledge Base + S3 bucket in the console to stop OpenSearch charges.)

## Interview Talking Point
> "I deployed a support assistant on Bedrock using managed RAG via Knowledge Bases —
> documents in S3 are auto-chunked, embedded with Titan, and stored in OpenSearch
> Serverless. The Lambda calls `retrieve_and_generate` for a grounded, cited answer, and
> falls back to direct `Converse` when I manage retrieval myself. It's wired into Amazon
> Connect via a Lambda invoke block for voice/chat."
