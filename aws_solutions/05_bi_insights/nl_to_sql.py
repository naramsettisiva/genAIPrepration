#!/usr/bin/env python3
"""
Solution 5: BI Insights — Natural Language to SQL (AWS Bedrock + Athena)
=======================================================================
Let non-technical users query business data in plain English. Claude translates
the question to SQL (grounded in your schema), Athena runs it against your S3
data lake, and Claude turns the results into a narrative insight.

This is the AWS-native version of the "MCP server for BI" pattern.

Flow: question -> Claude (NL->SQL with schema context) -> safety check
      -> Athena query -> Claude (results -> narrative) -> answer

Prereqs: Bedrock (Claude), Athena + Glue catalog over S3 data, an Athena results bucket.
Run: python3 nl_to_sql.py   (SQL generation runs; Athena execution needs a real DB)
"""

import boto3
import json
import time

REGION = "us-east-1"
LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
ATHENA_DB = "logistics"                       # your Glue/Athena database
ATHENA_OUTPUT = "s3://my-athena-results/"     # your Athena results bucket

# Schema context the LLM uses to generate correct SQL (enrich with business meaning)
SCHEMA_CONTEXT = """
Table: shipments
  - shipment_id (string)
  - origin_region (string): Northeast, Southeast, Midwest, West, Southwest
  - dest_region (string)
  - pickup_time (timestamp)
  - delivery_time (timestamp)
  - status (string): delivered, in_transit, delayed
Metric definitions:
  - delivery_hours = date_diff('hour', pickup_time, delivery_time)
"""

_bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def generate_sql(question: str) -> str:
    prompt = (
        f"Given this schema:\n{SCHEMA_CONTEXT}\n\n"
        f"Generate an Athena (Presto SQL) query to answer: {question}\n"
        f"Rules: SELECT only; always add a LIMIT (max 1000); use date filters where "
        f"relevant. Return ONLY the SQL, no explanation, no markdown fences."
    )
    resp = _bedrock.converse(
        modelId=LLM_MODEL,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.0},
    )
    sql = resp["output"]["message"]["content"][0]["text"].strip()
    return sql.replace("```sql", "").replace("```", "").strip()


def is_safe(sql: str) -> bool:
    """Only allow read-only SELECT queries."""
    s = sql.strip().upper()
    forbidden = ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "MERGE")
    return s.startswith("SELECT") and not any(f in s for f in forbidden)


def run_athena(sql: str):
    """Execute the SQL against Athena and return rows."""
    athena = boto3.client("athena", region_name=REGION)
    qid = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DB},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )["QueryExecutionId"]
    # Poll for completion
    while True:
        state = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        return None
    rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
    return rows


def narrate(question: str, rows) -> str:
    prompt = (
        f"Question: {question}\nQuery results: {json.dumps(rows)[:1500]}\n\n"
        f"Summarize the answer in 2-3 sentences with the key insight. Suggest one useful "
        f"follow-up question."
    )
    resp = _bedrock.converse(
        modelId=LLM_MODEL,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 250, "temperature": 0.3},
    )
    return resp["output"]["message"]["content"][0]["text"]


def ask(question: str):
    sql = generate_sql(question)
    print(f"  Generated SQL:\n    {sql}")
    if not is_safe(sql):
        print("  ⚠️  Query blocked by safety check (non-SELECT).")
        return
    print("  ✅ Passed safety check (read-only).")
    # Execution requires a real Athena DB; guarded so the demo runs offline.
    if ATHENA_OUTPUT.startswith("s3://my-athena-results"):
        print("  (Set ATHENA_DB/ATHENA_OUTPUT to real values to execute + narrate.)")
        return
    rows = run_athena(sql)
    if rows:
        print("\n  Insight:\n   ", narrate(question, rows))


def main():
    print("=" * 68)
    print("Solution 5: BI Insights — NL to SQL (Bedrock + Athena)")
    print("=" * 68)
    for q in ["What is the average delivery time by region this month?",
              "Which region has the most delayed shipments?"]:
        print(f"\nQuestion: {q}")
        ask(q)


if __name__ == "__main__":
    main()
