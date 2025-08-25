import openai
import json
import faiss
import numpy as np
from typing import List
import json


# Use OpenAI API key from environment variable
import os
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=OPENAI_API_KEY)

import os
input_path = os.path.join(os.path.dirname(__file__), "input.json")
with open(input_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# ----- Step 2: Create embeddings -----
def get_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

# Build vector store (FAISS)
dimension = 3072  # dimension of text-embedding-3-small
index = faiss.IndexFlatL2(dimension)

# Store mapping of IDs to embeddings
id_map = []
for article in raw_data["articles"]:
    emb = get_embedding(article["body"])
    index.add(np.array([emb]).astype('float32'))
    id_map.append(article["id"])

print(f"Stored {len(id_map)} articles in FAISS index.")

# ----- Step 3: Semantic search -----
def semantic_search(query: str, top_k: int = 2):
    q_emb = get_embedding(query)
    D, I = index.search(np.array([q_emb]).astype('float32'), top_k)
    results = [raw_data["articles"][i] for i in I[0]]
    return results

# Example: user query
query = "best practices for dog vaccinations"
results = semantic_search(query)
print("\nTop search results:")
for r in results:
    print("-", r["title"])

# ----- Step 4: Clean & structure with GPT -----
def ai_clean_and_structure(article_text):
    prompt = f"""
    You are an ETL agent. Clean and structure this knowledge base article.
    Return JSON with:
    - title
    - summary
    - key_entities
    - category
    - last_updated (if found or 'unknown')

    Article:
    {article_text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

structured_output = [ai_clean_and_structure(r["body"]) for r in results]

print("\n Structured Results:")
print(json.dumps(structured_output, indent=2))


# Example feedback loop update
def update_index_with_feedback(query, article_id, feedback):
    if feedback == "helpful":
        # boost this article's embedding in the index
        article = [a for a in raw_data["articles"] if a["id"] == article_id][0]
        emb = get_embedding(article["body"])
        # add duplicate (or weighted version) to FAISS index
        index.add(np.array([emb]).astype('float32'))
    elif feedback == "not_helpful":
        # log for review
        flagged_articles.append(article_id)

# Later, you can refresh flagged articles
def refresh_articles():
    for aid in flagged_articles:
        article = [a for a in raw_data["articles"] if a["id"] == aid][0]
        # Ask GPT to re-clean or enrich metadata
        improved = ai_clean_and_structure(article["body"])
        # re-embed and update FAISS
        emb = get_embedding(improved["summary"])
        index.add(np.array([emb]).astype('float32'))


