"""
Test script for the RAG Food System
Runs predefined queries and displays results
"""

import os
import json
from upstash_vector import Index
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Constants
JSON_FILE = "foods.json"
LLM_MODEL = "llama-3.1-8b-instant"

# Setup Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Setup Upstash Vector
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

def rag_query(question):
    """Run a RAG query and return the answer"""
    # Query with automatic embedding
    results = index.query(
        data=question,
        top_k=3,
        include_metadata=True
    )
    
    # Extract documents
    top_docs = [r.metadata["original_text"] for r in results]
    top_ids = [r.id for r in results]

    # Show retrieved documents
    print("\n📚 Retrieved Context:")
    for i, doc in enumerate(top_docs):
        print(f"   [{top_ids[i]}] {doc[:100]}...")

    # Build prompt
    context = "\n".join(top_docs)
    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

    # Generate answer with Groq
    completion = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions about food based on the provided context. Be concise and accurate."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=False
    )

    return completion.choices[0].message.content.strip()


# Test Queries
test_queries = [
    "How is Biryani prepared and what are its ingredients?",
    "What are some high-protein vegetarian Indian dishes?",
    "Which foods are popular in South India?",
    "What are good vegan options in Indian cuisine?",
    "Tell me about desserts with cardamom"
]

print("=" * 70)
print("🧪 RAG FOOD SYSTEM - TEST RESULTS")
print("=" * 70)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"🔍 QUERY {i}: {query}")
    print("-" * 70)
    
    try:
        answer = rag_query(query)
        print(f"\n🤖 ANSWER:\n{answer}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ Testing Complete!")
print("=" * 70)
