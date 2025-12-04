# 🧠 RAG-Food: Serverless Retrieval-Augmented Generation

This is a **fully serverless RAG (Retrieval-Augmented Generation)** demo using:

- ✅ [Upstash Vector](https://upstash.com/vector) for embeddings & semantic search (cloud-hosted)
- ✅ [Groq Cloud API](https://groq.com/) for ultra-fast LLM inference
- ✅ Built-in embedding model: `mixedbread-ai/mxbai-embed-large-v1`
- ✅ LLM model: `llama-3.1-8b-instant`
- ✅ A food dataset with 75 items (Indian, Asian, global cuisines)

**No local servers required!** Everything runs in the cloud.

---

## 🎯 What This Does

This app allows you to ask questions like:

- "Which Indian dish uses chickpeas?"
- "What dessert is made from milk and soaked in syrup?"
- "What is masala dosa made of?"
- "Tell me about Japanese food"

It **does not rely on the LLM's built-in memory**. Instead, it:

1. **Stores your custom text data** (about food) in Upstash Vector with automatic embeddings
2. For any question, it:
   - Sends your question to Upstash Vector (auto-embedded)
   - Finds relevant context via semantic search
   - Passes that context + question to Groq's LLM
3. Returns a natural-language answer grounded in your data.

---

## 📦 Requirements

### ✅ API Keys Needed

1. **Upstash Vector** - Get free credentials at [console.upstash.com](https://console.upstash.com)
   - Create a Vector index with model: `mixedbread-ai/mxbai-embed-large-v1`
   
2. **Groq API Key** - Get free API key at [console.groq.com](https://console.groq.com)

### ✅ Software

- Python 3.8+
- Internet connection

---

## 🛠️ Installation & Setup

### 1. Clone or download this repo

```bash
git clone https://github.com/yourname/rag-food
cd rag-food
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Install Python dependencies

Install from the requirements file:

```bash
pip install -r information.txt
```

Or install the core packages manually:

```bash
pip install upstash-vector groq python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
UPSTASH_VECTOR_REST_URL=https://your-index.upstash.io
UPSTASH_VECTOR_REST_TOKEN=your-upstash-token
GROQ_API_KEY=gsk_your_groq_api_key
```

### 5. Run the RAG app

```bash
python rag_run.py
```

On first run, it will:
* Upload all 75 food items to Upstash Vector
* Start an interactive Q&A session

---

## 📁 File Structure

```
rag-food/
├── rag_run.py                  # Main app script
├── foods.json                  # Food knowledge base (75 items)
├── .env                        # API credentials (create this)
├── information.txt             # Python dependencies (pip freeze)
├── upstash_migration_prd.md    # Migration documentation
├── groq_migration_plan.md      # Groq migration documentation
└── README.md                   # This file
```

---

## 🧠 How It Works (Step-by-Step)

1. **Data** is loaded from `foods.json` (75 food items)
2. Each entry is sent to Upstash Vector (auto-embedded by built-in model)
3. When you ask a question:
   - The question is sent to Upstash Vector
   - Top 3 most relevant food items are retrieved
   - Context + question is sent to Groq's `llama-3.1-8b-instant`
   - The model answers using that info only

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR MACHINE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      rag_run.py                               │  │
│  │  - Upstash Vector client (embeddings + search)               │  │
│  │  - Groq client (LLM generation)                              │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUD SERVICES                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │   Upstash Vector     │    │        Groq Cloud API            │  │
│  │  • Auto embeddings   │    │  • llama-3.1-8b-instant          │  │
│  │  • Semantic search   │    │  • ~500 tokens/sec               │  │
│  │  • 75 food docs      │    │  • Free tier available           │  │
│  └──────────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Example Usage

```
🧠 RAG is ready. Ask a question (type 'exit' to quit):

You: What is biryani?

🧠 Retrieving relevant information...

🔹 Source 1 (ID: 5):
    "Biryani is a flavorful Indian rice dish made with spices, rice, and usually meat or vegetables."

📚 Most relevant pieces of information found.

🤖: Biryani is a flavorful Indian rice dish originating from Hyderabad. It's made with aromatic spices, 
basmati rice, and typically includes meat (like chicken or lamb) or vegetables. It's classified as a 
main course dish.
```

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Serverless** | No local servers needed |
| **Auto Embeddings** | Upstash handles vectorization |
| **Fast LLM** | Groq's LPU provides ~500 tokens/sec |
| **Free Tiers** | Both services have generous free tiers |
| **75 Foods** | Covers Indian, Asian, Middle Eastern, and more |

---

## 💡 Next Ideas

* Add a web UI with Gradio or Streamlit
* Expand dataset with more cuisines
* Add metadata filtering (by region, type)
* Implement conversation history

---

## 👨‍🍳 Credits

Made by Callum using:

* [Upstash Vector](https://upstash.com/vector) - Serverless vector database
* [Groq](https://groq.com) - Ultra-fast LLM inference
* [mixedbread-ai/mxbai-embed-large-v1](https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1) - Embedding model
* Global food inspiration 🍛🍣🥟🌮

