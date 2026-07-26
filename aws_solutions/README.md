# AWS Deployable Solutions — 6 GenAI Use Cases

Complete, deployable reference implementations for six production GenAI patterns on the
**AWS tech stack**. Each solution has working code, an Infrastructure-as-Code template
(AWS SAM / CloudFormation), and step-by-step deployment instructions.

| # | Solution | Core AWS Services | Folder |
|---|----------|-------------------|--------|
| 1 | AI-Powered Customer Support | Bedrock Agents, Knowledge Bases, Lambda, Connect | [01_ai_customer_support](01_ai_customer_support/) |
| 2 | Case Categorization | Bedrock (Titan Embeddings + Claude), OpenSearch Serverless, Lambda | [02_case_categorization](02_case_categorization/) |
| 3 | AI Summaries | Bedrock (Claude), Comprehend (PII), Lambda | [03_ai_summaries](03_ai_summaries/) |
| 4 | TMS Automation (Agent + Tools) | Bedrock Agents, Action Groups, Lambda, DynamoDB | [04_tms_agent](04_tms_agent/) |
| 5 | BI Insights (NL → SQL) | Bedrock (Claude), Athena, S3, Lambda | [05_bi_insights](05_bi_insights/) |
| 6 | GenAI Adoption Program | Facilitator kit (workshops + templates) | [06_genai_adoption](06_genai_adoption/) |

---

## Prerequisites (one-time setup)

### 1. AWS Account & CLI
```bash
aws --version                       # AWS CLI v2
aws configure                       # set credentials + default region (e.g. us-east-1)
aws sts get-caller-identity         # verify identity
```

### 2. Enable Amazon Bedrock model access
Bedrock models are **opt-in per account/region**:
1. Open the **Amazon Bedrock console** → **Model access** (left nav)
2. Click **Manage model access** / **Enable specific models**
3. Enable at minimum:
   - **Anthropic Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`) — reasoning/generation
   - **Amazon Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`) — embeddings for RAG
   - **Amazon Nova** models (optional, cheaper routing)
4. Wait for status **Access granted** (usually instant to a few minutes)

### 3. Install AWS SAM CLI (for deployment)
```bash
# macOS
brew install aws-sam-cli
# or pip
pip install aws-sam-cli
sam --version
```

### 4. Python 3.10+ and dependencies
```bash
python3 --version
pip install boto3
```

---

## Deployment Pattern (common to all)

Each solution folder follows the same flow:
```bash
cd 0X_solution_name
pip install -r requirements.txt

# Option A: quick local test against Bedrock (needs AWS creds)
python3 <script>.py

# Option B: deploy serverless infra
sam build
sam deploy --guided        # first time: sets stack name, region, confirms IAM
```

---

## Cost & Safety Notes

- **Bedrock is pay-per-token.** These demos use minimal tokens, but always check
  [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/). Set up billing alerts.
- **OpenSearch Serverless** (Solution 2) has a minimum OCU cost — tear down when done:
  `sam delete`.
- **IAM least privilege:** templates grant only the permissions each function needs.
- **Region:** use a region where Bedrock + your chosen models are available (e.g. `us-east-1`, `us-west-2`).
- **Tear down** any stack when finished: `sam delete --stack-name <name>`.

---

## GCP Equivalents (for reference)

Every solution maps to GCP: Bedrock → **Vertex AI / Gemini**, Titan Embeddings →
**Vertex AI Embeddings**, OpenSearch → **Vertex AI Vector Search**, Athena → **BigQuery**,
Lambda → **Cloud Functions / Cloud Run**. Architecture and patterns are identical.
