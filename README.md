# 🧠 RAG-Food: Serverless Retrieval-Augmented Generation

**Author:** [Aniraj1]  
**Date:** December 2025  
**Course:** AI Builder Internship - Week 2

This is a **fully serverless RAG (Retrieval-Augmented Generation)** demo using:

- ✅ [Upstash Vector](https://upstash.com/vector) for embeddings & semantic search (cloud-hosted)
- ✅ [Groq Cloud API](https://groq.com/) for ultra-fast LLM inference
- ✅ Built-in embedding model: `mixedbread-ai/mxbai-embed-large-v1`
- ✅ LLM model: `llama-3.1-8b-instant`
- ✅ A food dataset with 75 items (Indian, Asian, global cuisines)

**No local servers required!** Everything runs in the cloud.

---

## 🆕 Enhanced Food Items (15 Detailed Entries)

The following 15 food items have been enhanced with comprehensive descriptions (50+ words each), nutritional information, dietary classifications, and preparation methods:

| # | Food Item | Region | Type | Dietary Info |
|---|-----------|--------|------|--------------|
| 1 | **Banana** | Tropical | Fruit | Vegan, Gluten-Free |
| 2 | **Lemon** | Mediterranean | Fruit | Vegan, Keto-Friendly |
| 3 | **Chili Pepper** | Mexico, Asia | Spice | Vegan, Keto-Friendly |
| 4 | **Apple** | Global | Fruit | Vegan, Gluten-Free |
| 5 | **Biryani** | Hyderabad, India | Main Course | Gluten-Free |
| 6 | **Samosa** | North India | Snack | Vegetarian |
| 7 | **Paneer Butter Masala** | Punjab | Main Course | Vegetarian, High Protein |
| 8 | **Masala Dosa** | South India | Breakfast | Vegan, Probiotic |
| 9 | **Chole (Chana Masala)** | Punjab | Main Course | Vegan, High Protein |
| 10 | **Rasgulla** | Bengal | Dessert | Vegetarian |
| 11 | **Naan** | North India | Bread | Vegetarian |
| 12 | **Tandoori Chicken** | Punjab | Main Course | Keto-Friendly, High Protein |
| 13 | **Gulab Jamun** | India | Dessert | Vegetarian |
| 14 | **Pav Bhaji** | Mumbai | Snack | Vegetarian |
| 15 | **Raita** | India | Condiment | Probiotic, Gluten-Free |

Each enhanced entry includes:
- 📝 Detailed description (50+ words)
- 🥗 Nutritional highlights
- 🍽️ Preparation methods
- 🏷️ Dietary classifications

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

## 🧪 Sample Test Queries & Expected Responses

Here are 10 diverse queries to test the RAG system:

### 1. Specific Dish Inquiry
**Query:** "What is biryani and how is it prepared?"  
**Expected:** Details about layered rice dish, dum cooking, regional variations

### 2. Nutritional Question
**Query:** "Which foods are high in protein?"  
**Expected:** Chole, Paneer Butter Masala, Tandoori Chicken, lentil-based dishes

### 3. Cultural Cuisine Query
**Query:** "Tell me about South Indian breakfast foods"  
**Expected:** Masala Dosa with fermented batter, served with chutney and sambar

### 4. Dietary Restriction Search
**Query:** "What vegan options are available?"  
**Expected:** Masala Dosa, Chole, fruits, vegetables

### 5. Cooking Method Question
**Query:** "What foods are cooked in a tandoor?"  
**Expected:** Naan, Tandoori Chicken

### 6. Health Benefits Query
**Query:** "Which foods contain probiotics?"  
**Expected:** Masala Dosa (fermented), Raita (yogurt-based)

### 7. Regional Food Query
**Query:** "What are popular foods from Punjab?"  
**Expected:** Naan, Tandoori Chicken, Paneer Butter Masala, Lassi

### 8. Dessert Query
**Query:** "Tell me about Indian desserts"  
**Expected:** Rasgulla, Gulab Jamun with descriptions

### 9. Street Food Query
**Query:** "What street foods are popular in Mumbai?"  
**Expected:** Pav Bhaji with its history and preparation

### 10. Ingredient-Based Query
**Query:** "What dishes use chickpeas?"  
**Expected:** Chole, Hummus, Falafel

---

## 📸 Screenshots

*(Add your screenshots here showing the RAG system in action)*

1. System startup and document loading
2. Sample query about biryani
3. Nutritional query response
4. Vegan options search

---

## 🎓 Personal Learning Reflection

Working on this RAG (Retrieval-Augmented Generation) project has been an incredibly knowledgable journey into the world of AI-powered applications. Before this project, I understood LLMs conceptually, but building a complete RAG system from scratch gave me hands-on experience with the entire pipeline.

**Key Learnings:**

1. **Vector Embeddings:** I learned how text is converted into numerical vectors that capture semantic meaning. The concept that similar meanings cluster together in vector space was fascinating to see in action.

2. **Semantic Search:** Unlike keyword matching, semantic search understands intent. When I queried "foods that are good for health," the system found relevant results even without the exact word "healthy."

3. **Cloud Architecture:** Migrating from local ChromaDB and Ollama to Upstash Vector and Groq taught me about serverless architectures. The benefits of not managing infrastructure while gaining speed improvements were significant.

4. **Prompt Engineering:** Crafting the right prompts for the LLM to use retrieved context effectively required experimentation and iteration.

5. **Data Quality Matters:** Enhancing food descriptions with detailed information dramatically improved response quality.

This project reinforced that AI is a tool that augments human capabilities. The "retrieval" in RAG ensures responses are grounded in actual data, reducing hallucinations. I'm excited to apply these concepts to larger datasets and more complex use cases.

---

## 👨‍🍳 Credits

Made by Callum using:

* [Upstash Vector](https://upstash.com/vector) - Serverless vector database
* [Groq](https://groq.com) - Ultra-fast LLM inference
* [mixedbread-ai/mxbai-embed-large-v1](https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1) - Embedding model
* Global food inspiration 🍛🍣🥟🌮

