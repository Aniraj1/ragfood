# Ollama → Groq Cloud API Migration Plan

## Executive Summary

This document outlines the migration strategy for replacing local Ollama LLM inference with Groq Cloud API. The migration eliminates the need to run a local LLM server while providing faster inference speeds through Groq's specialized LPU (Language Processing Unit) hardware.

---

## 1. Architecture Comparison

### Before (Current Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOCAL MACHINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐         ┌──────────────────────────────────┐ │
│  │  Upstash Vector  │◀───────▶│         rag_run.py               │ │
│  │  (Cloud)         │         │                                  │ │
│  └──────────────────┘         └──────────────┬───────────────────┘ │
│                                              │                     │
│                                              ▼                     │
│                               ┌──────────────────────────────────┐ │
│                               │       Ollama Server              │ │
│                               │  - localhost:11434               │ │
│                               │  - llama3.2 model                │ │
│                               │  - Local GPU/CPU inference       │ │
│                               │  - Must be running               │ │
│                               └──────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Issues:
- Requires Ollama to be running locally
- Uses local GPU/CPU resources
- Model must be downloaded (~4GB+)
- Performance depends on local hardware
```

### After (Target Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOCAL MACHINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      rag_run.py                               │  │
│  │  - Upstash Vector client (embeddings)                        │  │
│  │  - Groq client (LLM generation)                              │  │
│  │  - No local servers required                                 │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                   HTTPS API   │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUD SERVICES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │   Upstash Vector     │    │        Groq Cloud API            │  │
│  │  ──────────────────  │    │  ────────────────────────────────│  │
│  │  • Embeddings        │    │  • Model: llama-3.1-8b-instant   │  │
│  │  • Semantic search   │    │  • LPU acceleration              │  │
│  │  • 75 food docs      │    │  • ~500 tokens/sec               │  │
│  └──────────────────────┘    │  • OpenAI-compatible API         │  │
│                              └──────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Benefits:
- No local LLM server needed
- Extremely fast inference (Groq LPU)
- Works on any machine with internet
- Fully serverless architecture
```

---

## 2. Key Differences Summary

| Aspect | Ollama (Before) | Groq (After) |
|--------|-----------------|--------------|
| **Hosting** | Local server | Cloud API |
| **Model** | llama3.2 | llama-3.1-8b-instant |
| **Authentication** | None | API key (Bearer token) |
| **Endpoint** | `localhost:11434/api/generate` | Groq REST API |
| **API Format** | Custom Ollama format | OpenAI-compatible |
| **Dependencies** | `requests` | `groq` SDK |
| **Speed** | Depends on hardware | ~500 tokens/sec (LPU) |
| **Cost** | Free (local compute) | Free tier + usage-based |
| **Offline** | ✅ Yes | ❌ No |

---

## 3. Detailed Implementation Plan

### Phase 1: Environment Setup

#### Step 1.1: Install Groq SDK
```bash
pip install groq
```

#### Step 1.2: Verify `.env` File
Ensure your `.env` file contains:
```env
GROQ_API_KEY=gsk_your_api_key_here
UPSTASH_VECTOR_REST_URL=https://your-index.upstash.io
UPSTASH_VECTOR_REST_TOKEN=your-token-here
```

### Phase 2: Code Migration

#### Step 2.1: Update Imports
```python
# REMOVE (if only used for Ollama):
import requests  # Keep if used elsewhere

# ADD:
from groq import Groq
```

#### Step 2.2: Update Constants
```python
# BEFORE:
LLM_MODEL = "llama3.2"

# AFTER:
LLM_MODEL = "llama-3.1-8b-instant"
```

#### Step 2.3: Initialize Groq Client
```python
# ADD after load_dotenv():
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

#### Step 2.4: Replace LLM Generation Code
```python
# BEFORE (Ollama):
response = requests.post("http://localhost:11434/api/generate", json={
    "model": LLM_MODEL,
    "prompt": prompt,
    "stream": False
})

data = response.json()
if "response" not in data:
    raise ValueError(f"Ollama error: {data}")

return data["response"].strip()

# AFTER (Groq):
completion = groq_client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that answers questions about food based on the provided context."
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
```

### Phase 3: Complete Migrated Code

```python
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

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Setup Upstash Vector
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

# Setup Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Check if data needs to be added
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
```

---

## 4. API Differences

### Request Format

| Feature | Ollama | Groq |
|---------|--------|------|
| Method | `POST /api/generate` | `client.chat.completions.create()` |
| Input | `{"prompt": "..."}` | `messages=[{role, content}]` |
| Model param | `model: "llama3.2"` | `model: "llama-3.1-8b-instant"` |
| Streaming | `stream: False` | `stream: False` |

### Response Format

```python
# Ollama response:
{
    "response": "The answer text...",
    "done": True
}

# Groq response:
ChatCompletion(
    choices=[
        Choice(
            message=ChatCompletionMessage(
                content="The answer text...",
                role="assistant"
            )
        )
    ],
    usage=CompletionUsage(
        prompt_tokens=150,
        completion_tokens=50,
        total_tokens=200
    )
)
```

---

## 5. Error Handling Strategies

### Comprehensive Error Handling

```python
from groq import Groq, APIError, RateLimitError, APIConnectionError

def safe_groq_generate(client, prompt, model, max_retries=3):
    """Generate with retry logic and error handling."""
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful food assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=1024
            )
            return completion.choices[0].message.content.strip()
        
        except RateLimitError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"⏳ Rate limited. Waiting {wait_time}s...")
            import time
            time.sleep(wait_time)
            
        except APIConnectionError as e:
            print(f"🌐 Connection error: {e}")
            if attempt == max_retries - 1:
                raise
                
        except APIError as e:
            print(f"❌ API error: {e}")
            raise
    
    raise Exception("Max retries exceeded")
```

### Common Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| `RateLimitError` | Too many requests | Exponential backoff |
| `APIConnectionError` | Network issues | Retry with backoff |
| `AuthenticationError` | Invalid API key | Check `.env` file |
| `InvalidRequestError` | Bad parameters | Validate input |

---

## 6. Rate Limiting Considerations

### Groq Free Tier Limits

| Limit Type | Value |
|------------|-------|
| Requests per minute | 30 |
| Requests per day | 14,400 |
| Tokens per minute | 6,000 |
| Tokens per day | 500,000 |

### Rate Limit Handling

```python
import time
from functools import wraps

def rate_limit_handler(max_retries=3, base_delay=1):
    """Decorator for handling rate limits."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"⏳ Rate limited. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        raise
            return None
        return wrapper
    return decorator

@rate_limit_handler(max_retries=3)
def generate_answer(prompt):
    # ... generation code
    pass
```

---

## 7. Cost Implications

### Ollama (Local) Costs

| Item | Cost |
|------|------|
| Software | Free |
| Compute | Local GPU/CPU |
| Model download | One-time ~4GB |
| **Total** | **$0 (electricity only)** |

### Groq Cloud Costs

| Plan | Price |
|------|-------|
| Free tier | $0/month (with limits) |
| Pay-as-you-go | ~$0.05/1M input tokens |
| | ~$0.10/1M output tokens |

### Cost Estimation for This Project

For a food RAG with ~75 documents:
- Average prompt: ~200 tokens
- Average response: ~100 tokens
- 100 queries/day = ~30K tokens/day

**Estimated cost: $0/month** (well within free tier)

---

## 8. Fallback Strategies

### Option 1: Dual Provider Support

```python
import os
from groq import Groq, APIError

def get_llm_response(prompt, prefer_groq=True):
    """Try Groq first, fall back to Ollama if needed."""
    
    if prefer_groq:
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1024
            )
            return completion.choices[0].message.content.strip()
        except (APIError, Exception) as e:
            print(f"⚠️ Groq failed: {e}. Falling back to Ollama...")
    
    # Fallback to Ollama
    import requests
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": False},
            timeout=60
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        raise Exception(f"Both Groq and Ollama failed: {e}")
```

### Option 2: Model Fallback Chain

```python
GROQ_MODELS = [
    "llama-3.1-8b-instant",    # Primary (fastest)
    "llama-3.3-70b-versatile", # Fallback (more capable)
    "mixtral-8x7b-32768"       # Last resort
]

def generate_with_fallback(client, prompt):
    for model in GROQ_MODELS:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1024
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ {model} failed: {e}")
            continue
    raise Exception("All models failed")
```

---

## 9. Testing Approach

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

def test_rag_query_returns_answer():
    """Test that RAG query returns a non-empty answer."""
    with patch('groq.Groq') as MockGroq:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test answer"))]
        mock_client.chat.completions.create.return_value = mock_response
        MockGroq.return_value = mock_client
        
        answer = rag_query("What is biryani?")
        assert len(answer) > 0

def test_groq_api_error_handling():
    """Test error handling when Groq API fails."""
    with patch('groq.Groq') as MockGroq:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        MockGroq.return_value = mock_client
        
        with pytest.raises(Exception):
            rag_query("test question")
```

### Integration Test

```python
def test_full_rag_pipeline():
    """End-to-end test of the RAG pipeline."""
    questions = [
        ("What is biryani?", ["rice", "spice", "Indian"]),
        ("Tell me about sushi", ["Japanese", "fish", "rice"]),
        ("What is a banana?", ["fruit", "yellow", "sweet"])
    ]
    
    for question, expected_keywords in questions:
        answer = rag_query(question)
        assert any(kw.lower() in answer.lower() for kw in expected_keywords), \
            f"Expected one of {expected_keywords} in answer for '{question}'"
```

---

## 10. Performance Comparison

### Expected Performance

| Metric | Ollama (Local) | Groq (Cloud) |
|--------|----------------|--------------|
| Latency (first token) | 500-2000ms | 50-100ms |
| Throughput | 20-50 tok/s | 500+ tok/s |
| Cold start | None (if running) | None (serverless) |
| Consistency | Varies by hardware | Consistent |

### Groq's LPU Advantage

Groq uses custom Language Processing Units (LPUs) designed specifically for LLM inference:
- **10x faster** than GPU-based inference
- **Deterministic latency** (no variance)
- **No batching delays**

---

## 11. Migration Checklist

### Pre-Migration
- [ ] Get Groq API key from [console.groq.com](https://console.groq.com)
- [ ] Add `GROQ_API_KEY` to `.env` file
- [ ] Install `groq` package
- [ ] Backup current `rag_run.py`

### Code Changes
- [ ] Update imports (add `from groq import Groq`)
- [ ] Update `LLM_MODEL` constant
- [ ] Initialize Groq client
- [ ] Replace `requests.post()` with Groq SDK call
- [ ] Update response parsing
- [ ] Add error handling

### Post-Migration
- [ ] Test with sample questions
- [ ] Verify answer quality
- [ ] Monitor API usage in Groq console
- [ ] Remove `requests` import if not needed elsewhere

---

## 12. Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `rag_run.py` | Modify | Replace Ollama with Groq |
| `.env` | Verify | Ensure `GROQ_API_KEY` exists |
| `requirements.txt` | Add | `groq` package |

---

## Summary

This migration moves LLM inference from local Ollama to Groq Cloud API:

**Benefits:**
- ⚡ **10x faster inference** (Groq LPU vs local GPU)
- 🚀 **No local server required** (fully serverless)
- 💻 **Works on any machine** (no GPU needed)
- 🔄 **Consistent performance** (no hardware variance)

**Trade-offs:**
- 🌐 Requires internet connection
- 💰 Usage-based pricing (free tier available)
- 🔐 API key management required

For a food RAG demo with moderate usage, the free tier is more than sufficient.
