#!/usr/bin/env python3
"""
Lab 5b: LangChain Patterns — Chains, RAG, Agents
=================================================
LangChain is the most popular framework for building LLM apps. It gives you
composable building blocks so you don't reinvent RAG, agents, memory, etc.

This file demonstrates the KEY LANGCHAIN PATTERNS with annotated code. The
structure runs with a mock LLM (no API key). Swap the mock for a real LLM
(Bedrock/Vertex/OpenAI) and it's production code.

Patterns covered (all tied to your use cases):
  1. Chains         -> multi-step pipelines (classify -> route -> respond)
  2. RAG chain      -> retrieval-augmented Q&A
  3. Agent + tools  -> the TMS automation pattern
  4. Memory         -> multi-turn conversations

Run: python3 langchain_patterns.py
"""

# ---------------------------------------------------------------------------
# MOCK LLM — so this runs without an API key. In production you'd use:
#   from langchain_aws import ChatBedrock        # AWS
#   from langchain_google_vertexai import ChatVertexAI   # GCP / HealthConnect (sample)
#   from langchain_openai import ChatOpenAI      # OpenAI
# ---------------------------------------------------------------------------
class MockLLM:
    """Simulates an LLM so the patterns run offline."""
    def invoke(self, prompt):
        p = str(prompt).lower()
        if "classify" in p or "category" in p:
            if "invoice" in p or "charge" in p or "bill" in p:
                return "billing dispute"
            if "late" in p or "delay" in p:
                return "shipment delay"
            return "general inquiry"
        if "summarize" in p:
            return "Customer reported a delayed pickup; agent rescheduled and applied credit."
        return "Based on the provided context, here is a grounded answer."


# ===========================================================================
# PATTERN 1: CHAINS  (prompt template -> LLM -> output parser)
# Use case: case categorization pipeline
# ===========================================================================
def pattern_chains():
    print("\n" + "=" * 70)
    print("PATTERN 1: CHAINS (classify a support case)")
    print("=" * 70)
    print("""
    # --- LangChain code (LCEL - LangChain Expression Language) ---
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_aws import ChatBedrock

    prompt = ChatPromptTemplate.from_template(
        "Classify this support case into a category: {case}"
    )
    llm = ChatBedrock(model_id="anthropic.claude-3-sonnet")
    chain = prompt | llm | StrOutputParser()   # <-- the "|" composes the chain

    result = chain.invoke({"case": "I was charged twice on my invoice"})
    """)
    # Simulated execution:
    llm = MockLLM()
    case = "I was charged twice on my invoice"
    prompt = f"Classify this support case into a category: {case}"
    result = llm.invoke(prompt)
    print(f"  INPUT:  '{case}'")
    print(f"  OUTPUT: '{result}'")
    print("  💡 The '|' pipe operator composes reusable, testable pipelines")


# ===========================================================================
# PATTERN 2: RAG CHAIN  (retriever + prompt + LLM)
# Use case: member Q&A grounded in benefit documents
# ===========================================================================
def pattern_rag():
    print("\n" + "=" * 70)
    print("PATTERN 2: RAG CHAIN (grounded Q&A over documents)")
    print("=" * 70)
    print("""
    # --- LangChain RAG in ~10 lines ---
    from langchain_community.vectorstores import OpenSearchVectorSearch
    from langchain_aws import BedrockEmbeddings, ChatBedrock
    from langchain_core.prompts import ChatPromptTemplate

    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2")
    vectorstore = OpenSearchVectorSearch(embedding_function=embeddings, ...)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_template(
        "Answer using ONLY this context:\\n{context}\\n\\nQuestion: {question}"
    )
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt | ChatBedrock(...) | StrOutputParser()
    )
    answer = rag_chain.invoke("What is the specialist copay?")
    """)
    # Simulated: retriever returns a chunk, LLM answers from it
    retrieved = "Specialist Visit: $50 copay. Referral required."
    question = "What is the specialist copay?"
    print(f"  RETRIEVED CONTEXT: '{retrieved}'")
    print(f"  QUESTION: '{question}'")
    print(f"  GROUNDED ANSWER: 'The specialist copay is $50, and a referral is required.'")
    print("  💡 LangChain wires retriever->prompt->LLM so you don't build RAG from scratch")


# ===========================================================================
# PATTERN 3: AGENT + TOOLS  (the TMS automation pattern, framework version)
# Use case: agent that calls tools to take actions
# ===========================================================================
def pattern_agent():
    print("\n" + "=" * 70)
    print("PATTERN 3: AGENT + TOOLS (autonomous multi-step actions)")
    print("=" * 70)
    print("""
    # --- LangChain agent with tools ---
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_core.tools import tool

    @tool
    def check_shipment(shipment_id: str) -> str:
        \"\"\"Check the status of a shipment.\"\"\"
        return tms_api.get_status(shipment_id)

    @tool
    def reschedule_pickup(shipment_id: str, new_date: str) -> str:
        \"\"\"Reschedule a pickup to a new date.\"\"\"
        return tms_api.reschedule(shipment_id, new_date)

    tools = [check_shipment, reschedule_pickup]
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)

    executor.invoke({"input": "Reschedule pickup SH-001 to Thursday"})
    # Agent autonomously: checks status -> validates -> reschedules
    """)
    print("  💡 Same ReAct pattern as Lab 2, but LangChain handles the orchestration loop")
    print("  💡 LangGraph (LangChain's newer library) adds stateful, multi-agent workflows")


# ===========================================================================
# PATTERN 4: MEMORY  (multi-turn conversation state)
# Use case: member conversation that remembers context
# ===========================================================================
def pattern_memory():
    print("\n" + "=" * 70)
    print("PATTERN 4: MEMORY (multi-turn conversations)")
    print("=" * 70)
    print("""
    # --- LangChain conversation memory ---
    from langchain_core.runnables.history import RunnableWithMessageHistory

    # Wraps a chain so it remembers prior turns per session
    chain_with_memory = RunnableWithMessageHistory(
        chain, get_session_history,
        input_messages_key="input", history_messages_key="history"
    )
    # Turn 1: "What's my specialist copay?"  -> "$50"
    # Turn 2: "And for the ER?"  <- remembers we're talking about copays
    """)
    print("  💡 Memory lets the member say 'and for the ER?' without repeating context")


def main():
    print("\n" + "#" * 70)
    print("# LAB 5b: LANGCHAIN PATTERNS")
    print("#" * 70)
    print("\nLangChain = composable building blocks for LLM apps.")
    print("The code shown is real LangChain; execution is simulated (no API key).\n")

    pattern_chains()
    pattern_rag()
    pattern_agent()
    pattern_memory()

    print("\n" + "=" * 70)
    print("WHEN TO USE LANGCHAIN (interview-ready judgment):")
    print("=" * 70)
    print("""
  ✅ USE IT:  rapid prototyping, standard patterns (RAG, agents, memory),
             swapping LLM providers, rich ecosystem of integrations
  ⚠️  CAUTION: adds abstraction layers; for simple use cases raw SDK is clearer;
             can be hard to debug; production teams sometimes outgrow it
  ALTERNATIVES: LlamaIndex (RAG-focused), raw Bedrock/Vertex SDK,
             LangGraph (complex stateful agents), Semantic Kernel (MS)
    """)


if __name__ == "__main__":
    main()
