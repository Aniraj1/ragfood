# ChromaDB → Upstash Vector Migration Plan

## Executive Summary

This document outlines the migration strategy for replacing ChromaDB (local vector storage) with Upstash Vector (cloud-hosted serverless vector database) for the RAG Food application. The migration simplifies the architecture by eliminating local embedding generation (Ollama) and leveraging Upstash's built-in embedding models.

---

## 1. Architecture Comparison

### Before (Current Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOCAL MACHINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  foods.json  │───▶│  Ollama Server   │───▶│    ChromaDB      │  │
│  │   (75 items) │    │  (Embeddings)    │    │  (Local SQLite)  │  │
│  └──────────────┘    │  Port: 11434     │    │  ./chroma_db/    │  │
│                      │  mxbai-embed-    │    └────────┬─────────┘  │
│                      │  large           │             │            │
│                      └────────┬─────────┘             │            │
│                               │                       │            │
│                               ▼                       ▼            │
│                      ┌──────────────────────────────────┐          │
│                      │         rag_run.py               │          │
│                      │  - Manual embedding generation   │          │
│                      │  - ChromaDB client               │          │
│                      │  - Ollama LLM calls              │          │
│                      └──────────────────────────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Components:
- Ollama server (must be running locally)
- ChromaDB persistent storage (local files)
- Manual embedding generation via API calls
- 2 separate services to manage
```

### After (Target Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOCAL MACHINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐              ┌──────────────────────────────────┐ │
│  │  foods.json  │─────────────▶│         rag_run.py               │ │
│  │   (75 items) │              │  - Raw text upsert               │ │
│  └──────────────┘              │  - Upstash Vector client         │ │
│                                │  - Ollama LLM calls              │ │
│                                └──────────────┬───────────────────┘ │
│                                               │                     │
└───────────────────────────────────────────────┼─────────────────────┘
                                                │
                                    HTTPS API   │
                                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       UPSTASH CLOUD                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Upstash Vector Database                      │  │
│  │  ────────────────────────────────────────────────────────────│  │
│  │  • Model: mixedbread-ai/mxbai-embed-large-v1                 │  │
│  │  • Dimensions: 1024                                           │  │
│  │  • Sequence Length: 512 tokens                                │  │
│  │  • MTEB Score: 64.68                                          │  │
│  │  • Automatic vectorization on upsert & query                  │  │
│  │  • Cosine similarity search                                   │  │
│  │  • Serverless (no infrastructure management)                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Benefits:
- No local embedding server required
- Automatic vectorization (send raw text)
- Cloud-hosted, always available
- Single service to manage (just Ollama for LLM)
```

---

## 2. Key Differences Summary

| Aspect | ChromaDB (Before) | Upstash Vector (After) |
|--------|-------------------|------------------------|
| **Hosting** | Local (SQLite files) | Cloud (Serverless) |
| **Embedding** | Manual via Ollama API | Automatic (built-in model) |
| **Authentication** | None | API token required |
| **Data Storage** | `./chroma_db/` folder | Upstash cloud |
| **Dependencies** | `chromadb`, `requests` | `upstash-vector` |
| **Upsert Format** | `(id, embedding, document)` | `(id, raw_text, metadata)` |
| **Query Format** | `query_embeddings=[vector]` | `data="raw text query"` |
| **Startup** | Ollama + ChromaDB init | Just API connection |
| **Offline Support** | ✅ Yes | ❌ No (requires internet) |

---

## 3. Detailed Implementation Plan

### Phase 1: Environment Setup

#### Step 1.1: Install Dependencies
```bash
pip install upstash-vector python-dotenv
pip uninstall chromadb  # Optional: remove old dependency
```

#### Step 1.2: Verify `.env` File
Ensure your `.env` file contains:
```env
UPSTASH_VECTOR_REST_URL=https://your-index-url.upstash.io
UPSTASH_VECTOR_REST_TOKEN=your-token-here
```

### Phase 2: Code Migration

#### Step 2.1: Update Imports
```python
# REMOVE these:
import chromadb

# ADD these:
from upstash_vector import Index
from dotenv import load_dotenv
import os

load_dotenv()
```

#### Step 2.2: Replace Client Initialization
```python
# BEFORE (ChromaDB):
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# AFTER (Upstash Vector):
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)
```

#### Step 2.3: Remove Manual Embedding Function
```python
# DELETE this entire function:
def get_embedding(text):
    response = requests.post("http://localhost:11434/api/embeddings", json={
        "model": EMBED_MODEL,
        "prompt": text
    })
    return response.json()["embedding"]
```

#### Step 2.4: Update Upsert Logic
```python
# BEFORE (ChromaDB with manual embeddings):
for item in new_items:
    enriched_text = item["text"]
    if "region" in item:
        enriched_text += f" This food is popular in {item['region']}."
    if "type" in item:
        enriched_text += f" It is a type of {item['type']}."
    
    emb = get_embedding(enriched_text)
    
    collection.add(
        documents=[item["text"]],
        embeddings=[emb],
        ids=[item["id"]]
    )

# AFTER (Upstash with automatic embedding):
vectors_to_upsert = []
for item in food_data:
    enriched_text = item["text"]
    if "region" in item:
        enriched_text += f" This food is popular in {item['region']}."
    if "type" in item:
        enriched_text += f" It is a type of {item['type']}."
    
    vectors_to_upsert.append((
        item["id"],                           # id
        enriched_text,                        # raw text (auto-embedded)
        {                                     # metadata
            "original_text": item["text"],
            "region": item.get("region", ""),
            "type": item.get("type", "")
        }
    ))

# Batch upsert (more efficient)
index.upsert(vectors_to_upsert)
```

#### Step 2.5: Update Query Logic
```python
# BEFORE (ChromaDB):
def rag_query(question):
    q_emb = get_embedding(question)
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    top_docs = results['documents'][0]
    top_ids = results['ids'][0]
    # ... rest of function

# AFTER (Upstash):
def rag_query(question):
    results = index.query(
        data=question,           # Raw text query (auto-embedded)
        top_k=3,
        include_metadata=True
    )
    
    top_docs = [r.metadata["original_text"] for r in results]
    top_ids = [r.id for r in results]
    # ... rest of function
```

### Phase 3: Complete Migrated Code

```python
import os
import json
import requests
from upstash_vector import Index
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
JSON_FILE = "foods.json"
LLM_MODEL = "gemma3:1b"

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Setup Upstash Vector
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

# Check if data needs to be added (simple check)
info = index.info()
if info.vector_count == 0:
    print(f"🆕 Adding {len(food_data)} documents to Upstash Vector...")
    
    vectors_to_upsert = []
    for item in food_data:
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
    
    # Step 4: Show retrieved documents
    print("\n🧠 Retrieving relevant information...\n")
    for i, doc in enumerate(top_docs):
        print(f"🔹 Source {i + 1} (ID: {top_ids[i]}):")
        print(f"    \"{doc}\"\n")
    
    print("📚 Most relevant pieces of information found.\n")
    
    # Step 5: Build prompt
    context = "\n".join(top_docs)
    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""
    
    # Step 6: Generate with Ollama
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    })
    
    data = response.json()
    if "response" not in data:
        raise ValueError(f"Ollama error: {data}")
    
    return data["response"].strip()

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
```

---

## 4. API Differences and Implications

### Upsert API

| Feature | ChromaDB | Upstash Vector |
|---------|----------|----------------|
| Method | `collection.add()` | `index.upsert()` |
| Batch support | One at a time | Native batch (list of tuples) |
| Format | `documents=[], embeddings=[], ids=[]` | `[(id, data, metadata), ...]` |
| Embedding | Pre-computed vector required | Raw text (auto-embedded) |

### Query API

| Feature | ChromaDB | Upstash Vector |
|---------|----------|----------------|
| Method | `collection.query()` | `index.query()` |
| Input | `query_embeddings=[vector]` | `data="raw text"` |
| Results | `results['documents'][0]` | `[Result(id, score, metadata)]` |
| Top-K | `n_results=3` | `top_k=3` |

### Response Structure

```python
# ChromaDB response:
{
    'ids': [['1', '2', '3']],
    'documents': [['doc1', 'doc2', 'doc3']],
    'distances': [[0.1, 0.2, 0.3]]
}

# Upstash response (list of Result objects):
[
    Result(id='1', score=0.95, metadata={'original_text': '...', 'region': '...'}),
    Result(id='2', score=0.89, metadata={'original_text': '...', 'region': '...'}),
    Result(id='3', score=0.82, metadata={'original_text': '...', 'region': '...'})
]
```

---

## 5. Error Handling Strategies

### Recommended Error Handling Pattern

```python
from upstash_vector import Index
from upstash_vector.errors import UpstashError
import requests

def safe_upsert(index, vectors):
    """Safely upsert vectors with error handling."""
    try:
        index.upsert(vectors)
        return True
    except UpstashError as e:
        print(f"❌ Upstash error: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Network error: Cannot reach Upstash servers")
        return False

def safe_query(index, question, top_k=3):
    """Safely query with error handling."""
    try:
        results = index.query(
            data=question,
            top_k=top_k,
            include_metadata=True
        )
        return results
    except UpstashError as e:
        print(f"❌ Query error: {e}")
        return []
    except requests.exceptions.ConnectionError:
        print("❌ Network error: Cannot reach Upstash servers")
        return []

def validate_env():
    """Validate environment variables on startup."""
    url = os.getenv("UPSTASH_VECTOR_REST_URL")
    token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    
    if not url or not token:
        raise EnvironmentError(
            "Missing Upstash credentials. Set UPSTASH_VECTOR_REST_URL "
            "and UPSTASH_VECTOR_REST_TOKEN in .env file."
        )
    return url, token
```

### Common Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| `ConnectionError` | No internet or Upstash down | Check network, retry |
| `AuthenticationError` | Invalid token | Verify `.env` credentials |
| `RateLimitError` | Too many requests | Add exponential backoff |
| `ValidationError` | Invalid input format | Check data types |

---

## 6. Performance Considerations

### Latency Comparison

| Operation | ChromaDB (Local) | Upstash (Cloud) |
|-----------|------------------|-----------------|
| Upsert (single) | ~5-10ms | ~50-100ms |
| Upsert (batch 75) | ~500ms | ~200-400ms |
| Query | ~10-20ms | ~100-200ms |
| Embedding | ~200-500ms (Ollama) | Included in upsert/query |

### Optimization Tips

1. **Batch upserts**: Always use batch operations
   ```python
   # ❌ Bad: One at a time
   for item in items:
       index.upsert([(id, text, metadata)])
   
   # ✅ Good: Batch
   index.upsert([(id, text, metadata) for item in items])
   ```

2. **Connection reuse**: Create index client once at startup

3. **Caching**: For repeated queries, consider local caching

4. **Async operations**: Use `upstash-vector` async client for high-throughput

---

## 7. Cost Implications

### ChromaDB (Local) Costs

| Item | Cost |
|------|------|
| Software | Free (open-source) |
| Storage | Local disk space |
| Compute | Local CPU/RAM |
| Embedding | Ollama (free, but uses GPU/CPU) |
| **Total** | **$0 (hardware costs only)** |

### Upstash Vector Costs

| Plan | Vectors | Queries/day | Price |
|------|---------|-------------|-------|
| Free | 10,000 | 10,000 | $0/month |
| Pay as you go | - | - | $0.4/100K queries |

**For this project (75 food items)**:
- Storage: Well within free tier
- Queries: Likely within free tier for development
- **Estimated cost: $0/month** for typical usage

### When Costs Increase

- Large-scale production (millions of queries)
- Large datasets (>10K vectors)
- High-frequency real-time applications

---

## 8. Security Considerations

### API Key Management

```python
# ✅ GOOD: Load from environment
from dotenv import load_dotenv
load_dotenv()

index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

# ❌ BAD: Hardcoded credentials
index = Index(
    url="https://xxx.upstash.io",
    token="secret-token-here",  # NEVER DO THIS
)
```

### `.gitignore` Configuration

```gitignore
# Add to .gitignore
.env
*.env
.env.local
.env.*.local
```

### Security Checklist

- [ ] Store credentials in `.env` file (never in code)
- [ ] Add `.env` to `.gitignore`
- [ ] Use read-only tokens when possible
- [ ] Rotate tokens periodically
- [ ] Monitor Upstash dashboard for unusual activity
- [ ] Use HTTPS only (Upstash enforces this)

---

## 9. Migration Checklist

### Pre-Migration
- [ ] Create Upstash Vector index with `mixedbread-ai/mxbai-embed-large-v1` model
- [ ] Add credentials to `.env` file
- [ ] Install `upstash-vector` and `python-dotenv` packages
- [ ] Backup current ChromaDB data (optional)

### Code Changes
- [ ] Update imports (remove `chromadb`, add `upstash_vector`, `dotenv`)
- [ ] Replace client initialization
- [ ] Remove `get_embedding()` function
- [ ] Update upsert logic to use raw text
- [ ] Update query logic to use `data=` parameter
- [ ] Update result parsing (metadata access)
- [ ] Add error handling

### Post-Migration
- [ ] Test upsert with all 75 food items
- [ ] Test queries with sample questions
- [ ] Verify RAG responses match expected quality
- [ ] Remove `chroma_db/` folder (optional)
- [ ] Uninstall `chromadb` package (optional)

---

## 10. Rollback Plan

If issues arise, you can quickly rollback:

1. Keep the original `rag_run.py` as `rag_run_chroma.py`
2. Keep `chroma_db/` folder intact
3. Rollback: `python rag_run_chroma.py`

---

## 11. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `rag_run.py` | Modify | Main migration changes |
| `.env` | Create/Verify | Upstash credentials |
| `.gitignore` | Modify | Add `.env` |
| `requirements.txt` | Modify | Add `upstash-vector`, `python-dotenv` |
| `chroma_db/` | Delete (later) | No longer needed |

---

## Summary

This migration simplifies the RAG architecture by:
1. **Eliminating local embedding generation** (no more Ollama embedding calls)
2. **Moving to serverless infrastructure** (no local database files)
3. **Reducing complexity** (one less service to manage)
4. **Improving portability** (works from any machine with internet)

The trade-off is:
- Requires internet connectivity
- Introduces cloud dependency
- Small latency increase for queries

For a development/learning project with 75 documents, Upstash's free tier is more than sufficient.