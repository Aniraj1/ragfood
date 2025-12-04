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

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Setup Upstash Vector
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

# Check if data needs to be added
info = index.info()
if info.vector_count == 0:
    print(f"🆕 Adding {len(food_data)} documents to Upstash Vector...")
    
    vectors_to_upsert = []
    for item in food_data:
        # Enhance text with region/type
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."
        
        vectors_to_upsert.append((
            item["id"],
            enriched_text,
            {
                "original_text": item["text"],
                "region": item.get("region", ""),
                "type": item.get("type", "")
            }
        ))
    
    index.upsert(vectors_to_upsert)
    print("✅ Documents added successfully!")
else:
    print(f"✅ {info.vector_count} documents already in Upstash Vector.")

# RAG query
def rag_query(question):
    # Step 1 & 2: Query with automatic embedding
    results = index.query(
        data=question,
        top_k=3,
        include_metadata=True
    )
    
    # Step 3: Extract documents
    top_docs = [r.metadata["original_text"] for r in results]
    top_ids = [r.id for r in results]

    # Step 4: Show friendly explanation of retrieved documents
    print("\n🧠 Retrieving relevant information to reason through your question...\n")

    for i, doc in enumerate(top_docs):
        print(f"🔹 Source {i + 1} (ID: {top_ids[i]}):")
        print(f"    \"{doc}\"\n")

    print("📚 These seem to be the most relevant pieces of information to answer your question.\n")

    # Step 5: Build prompt from context
    context = "\n".join(top_docs)

    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

    # Step 6: Generate answer with Groq
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

    # Step 7: Return final result
    return completion.choices[0].message.content.strip()


# Interactive loop
print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
while True:
    question = input("You: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break
    try:
        answer = rag_query(question)
        print("🤖:", answer)
    except Exception as e:
        print(f"❌ Error: {e}")
