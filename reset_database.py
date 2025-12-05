"""
Script to reset and reload the Upstash Vector database with updated food data.
Run this after updating foods.json to refresh the embeddings.
"""

import os
import json
from upstash_vector import Index
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
JSON_FILE = "foods.json"

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Setup Upstash Vector
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

print("🗑️  Resetting Upstash Vector database...")

# Reset the index (delete all vectors)
index.reset()

print(f"🆕 Adding {len(food_data)} documents to Upstash Vector...")

vectors_to_upsert = []
for item in food_data:
    # Enhance text with additional metadata
    enriched_text = item["text"]
    if "region" in item:
        enriched_text += f" This food is popular in {item['region']}."
    if "type" in item:
        enriched_text += f" It is a type of {item['type']}."
    if "dietary" in item:
        enriched_text += f" Dietary info: {', '.join(item['dietary'])}."
    if "nutritional_highlights" in item:
        enriched_text += f" Nutritional benefits: {item['nutritional_highlights']}."
    
    vectors_to_upsert.append((
        item["id"],
        enriched_text,
        {
            "original_text": item["text"],
            "region": item.get("region", ""),
            "type": item.get("type", ""),
            "dietary": ", ".join(item.get("dietary", [])),
            "nutritional_highlights": item.get("nutritional_highlights", "")
        }
    ))

index.upsert(vectors_to_upsert)

print("✅ Database reset complete!")
print(f"📊 Total documents: {len(food_data)}")

# Verify
info = index.info()
print(f"🔢 Vector count in database: {info.vector_count}")
