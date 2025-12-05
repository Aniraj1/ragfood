# 🧪 RAG System Test Queries

This document contains 10 diverse test queries to validate the RAG-Food system.

## Test Execution Instructions

1. Activate virtual environment:
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

2. Run the RAG system:
   ```bash
   python rag_run.py
   ```

3. Enter each query and document the response

---

## Query Categories & Test Cases

### Category 1: Specific Dish Inquiries

#### Query 1.1
```
What is biryani and how is it prepared?
```
**Expected Response Topics:**
- Layered rice dish with meat/vegetables
- Dum cooking method (sealed pot)
- Saffron, ghee, and spices
- Regional variations (Hyderabadi, Lucknowi)

#### Query 1.2
```
Tell me about masala dosa
```
**Expected Response Topics:**
- Fermented rice and lentil crepe
- Filled with spiced potato
- South Indian breakfast
- Served with chutney and sambar

---

### Category 2: Nutritional Questions

#### Query 2.1
```
Which foods are high in protein?
```
**Expected Response Topics:**
- Chole (chickpeas)
- Paneer Butter Masala
- Tandoori Chicken
- Lentil-based dishes

#### Query 2.2
```
What foods contain probiotics?
```
**Expected Response Topics:**
- Masala Dosa (fermented batter)
- Raita (yogurt-based)
- Lassi (yogurt drink)

---

### Category 3: Cultural Cuisine Queries

#### Query 3.1
```
What are popular foods from Punjab?
```
**Expected Response Topics:**
- Tandoori Chicken
- Naan
- Paneer Butter Masala
- Lassi
- Butter Chicken

#### Query 3.2
```
Tell me about Japanese food
```
**Expected Response Topics:**
- Sushi
- Ramen
- Tempura
- Miso soup

---

### Category 4: Dietary Restriction Searches

#### Query 4.1
```
What vegan options are available?
```
**Expected Response Topics:**
- Masala Dosa
- Chole
- Fruits (banana, apple)
- Many vegetable dishes

#### Query 4.2
```
Which foods are gluten-free?
```
**Expected Response Topics:**
- Rice-based dishes (biryani, dosa)
- Tandoori chicken
- Raita
- Most Indian curries

---

### Category 5: Cooking Method Questions

#### Query 5.1
```
What foods are cooked in a tandoor?
```
**Expected Response Topics:**
- Naan bread
- Tandoori Chicken
- High-heat clay oven cooking
- Charred, smoky flavor

#### Query 5.2
```
What foods can be grilled or roasted?
```
**Expected Response Topics:**
- Tandoori items
- Kebabs
- Char siu (BBQ pork)

---

## Test Results Template

| Query # | Query Text | Response Summary | Quality (1-5) | Notes |
|---------|------------|------------------|---------------|-------|
| 1.1 | What is biryani... | | | |
| 1.2 | Tell me about masala dosa | | | |
| 2.1 | Which foods are high in protein? | | | |
| 2.2 | What foods contain probiotics? | | | |
| 3.1 | What are popular foods from Punjab? | | | |
| 3.2 | Tell me about Japanese food | | | |
| 4.1 | What vegan options are available? | | | |
| 4.2 | Which foods are gluten-free? | | | |
| 5.1 | What foods are cooked in a tandoor? | | | |
| 5.2 | What foods can be grilled? | | | |

---

## Success Criteria

- ✅ All queries return relevant context from the database
- ✅ LLM generates coherent answers based on context
- ✅ System handles diverse query types
- ✅ Response time is acceptable (< 5 seconds)
- ✅ No errors or crashes during testing
