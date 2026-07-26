# Solution 5: BI Insights — Natural Language to SQL

Let non-technical users query business data in plain English. Claude generates SQL from
your schema, Athena runs it against your S3 data lake, and Claude narrates the result.
This is the AWS-native version of the "MCP server for BI" pattern.

## Architecture

```
User: "Average delivery time by region this month?"
   │
   ▼
Lambda ──► Claude (NL -> SQL, grounded in schema context)
       ──► Safety check (SELECT-only, no mutations)
       ──► Amazon Athena (query S3 data lake via Glue catalog)
       ──► Claude (results -> narrative insight + follow-up)
       ──► answer
```

## AWS Services
- **Bedrock — Claude 3 Sonnet** — NL→SQL translation and result narration
- **Amazon Athena** — serverless SQL over S3 (Presto)
- **AWS Glue Data Catalog** — table/schema definitions
- **Amazon S3** — data lake + Athena query results
- **Lambda + API Gateway** — endpoint

## Safety (critical for NL→SQL)
- **SELECT-only enforcement** — reject INSERT/UPDATE/DELETE/DROP/etc.
- **Read-only IAM** — the Lambda's Athena/Glue role has no write/DDL permissions
- **LIMIT enforced** — prompt requires a LIMIT to prevent runaway scans
- **Schema-scoped** — only expose non-sensitive columns in the schema context
- **Show the SQL** — return the generated query so users can verify logic

## Deploy / Run

### Prereqs
1. Have data in **S3** with a **Glue** table (e.g. `logistics.shipments`)
2. Create an **Athena results S3 bucket**
3. Edit `nl_to_sql.py`: set `ATHENA_DB` and `ATHENA_OUTPUT`

### Local test (SQL generation runs; execution needs real Athena)
```bash
cd aws_solutions/05_bi_insights
pip install -r requirements.txt
python3 nl_to_sql.py
```

### IAM for the Lambda
```
bedrock:Converse, bedrock:InvokeModel
athena:StartQueryExecution, athena:GetQueryExecution, athena:GetQueryResults
glue:GetTable, glue:GetDatabase
s3:GetObject, s3:PutObject   (results bucket + data bucket, read-only on data)
```

## Interview Talking Point
> "I built a natural-language BI interface on AWS. Claude translates the question to
> Athena SQL using injected schema context with business-metric definitions, a safety
> layer enforces SELECT-only with read-only IAM, Athena runs it over the S3 data lake, and
> Claude narrates the result with a suggested follow-up. Non-technical stakeholders get
> instant, grounded answers without waiting on analysts — and we return the generated SQL
> for transparency."
