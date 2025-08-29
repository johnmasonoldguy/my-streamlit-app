
# --- Force Python to use certifi's CA bundle for all HTTPS requests ---
# import certifi, os
# os.environ["SSL_CERT_FILE"] = certifi.where()
# os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import json
import faiss
import numpy as np
import hashlib
from typing import List
from openai import OpenAI
from pathlib import Path

# Load environment variables from .env if present
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------- Step 0: Initialize client ----------------

# import httpx
# import certifi
import os

# Force all requests (including OpenAI and httpx) to use certifi's CA bundle
# os.environ["SSL_CERT_FILE"] = certifi.where()
# os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Patch httpx default client to always use certifi
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
# ---------------- Step 1: Sample raw KB data (Extract) ----------------
html_folder = Path("./app/backend/html_articles")
html_files = list(html_folder.glob("*.html"))

raw_data = {"articles": []}
for file in html_files:
    raw_data["articles"].append({
        "id": file.stem,
        "title": file.stem,
        "body": file.read_text(encoding="utf-8")
    })

# print progress
print(f"Processed {raw_data}") 

# ---------------- Step 2: Build Map (new vs unchanged) ----------------
# ---------------- Step 2: Build Change Map ----------------
try:
    with open("hash_map.json", "r") as f:
        stored_hashes = json.load(f)
except FileNotFoundError:
    stored_hashes = {}

def build_change_map(articles):
    to_process, skip = [], []
    new_hashes = {}

    for art in articles:
        aid = art["id"]
        text = art["body"]
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        new_hashes[aid] = h

        if aid not in stored_hashes or stored_hashes[aid] != h:
            to_process.append(aid)
        else:
            skip.append(aid)

    return {"to_process": to_process, "skip": skip, "new_hashes": new_hashes}

change_map = build_change_map(raw_data["articles"])
print("Change Map:", json.dumps(change_map, indent=2))

with open("hash_map.json", "w") as f:
    json.dump(change_map["new_hashes"], f, indent=2)

# ---------------- Step 3: AI Process (HTML -> DITA) ----------------
def get_embedding(text: str) -> List[float]:
    response = client.embeddings.create(input=text, model="text-embedding-3-large")
    return response.data[0].embedding

def html_to_dita(article_text: str):
    prompt = f"""
You are an ETL agent specializing in DITA authoring.
Transform the following HTML content into a DITA task structure using these elements:

- task, taskbody, prereq, context, steps, step, cmd, info, stepxmp, stepresult, result, postreq, p, ol, ul, li

Follow DITA 1.3 standards for formatting and nesting. Return only valid DITA XML.
HTML Content:
{article_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# Only process new/updated articles
to_process_articles = [a for a in raw_data["articles"] if a["id"] in change_map["to_process"]]
dita_folder = Path("./app/backend/dita_articles")
dita_folder.mkdir(exist_ok=True)

structured_outputs = []
for art in to_process_articles:
    dita_content = html_to_dita(art["body"])
    structured_outputs.append(dita_content)
    with open(dita_folder / f"{art['id']}.dita", "w", encoding="utf-8") as f:
        f.write(dita_content)

print(f"Saved {len(structured_outputs)} DITA files in {dita_folder}")

for art in raw_data["articles"]:
    dita_content = html_to_dita(art["body"])
    with open(dita_folder / f"{art['id']}_full.dita", "w", encoding="utf-8") as f:
        f.write(dita_content)
    print(f"Saved {art['id']}_full.dita")

# ---------------- Step 4: Load into FAISS index ----------------
dimension = 3072  # text-embedding-3-large
index = faiss.IndexFlatL2(dimension)
id_map = []

for art in raw_data["articles"]:
    emb = get_embedding(art["body"])
    index.add(np.array([emb]).astype('float32'))
    id_map.append(art["id"])

print(f"Stored {len(id_map)} articles in FAISS index.")

def semantic_search(query: str, top_k: int = 2):
    q_emb = get_embedding(query)
    D, I = index.search(np.array([q_emb]).astype('float32'), top_k)
    results = [raw_data["articles"][i] for i in I[0]]
    return results

# ---------------- Step 5: Feedback Loop ----------------
flagged_articles = []

def update_index_with_feedback(query, article_id, feedback):
    if feedback == "helpful":
        article = next(a for a in raw_data["articles"] if a["id"] == article_id)
        emb = get_embedding(article["body"])
        index.add(np.array([emb]).astype('float32'))
    elif feedback == "not_helpful":
        flagged_articles.append(article_id)

def refresh_articles():
    for aid in flagged_articles:
        article = next(a for a in raw_data["articles"] if a["id"] == aid)
        improved = html_to_dita(article["body"])
        emb = get_embedding(improved)
        index.add(np.array([emb]).astype('float32'))

# ---------------- Example Usage ----------------
query = "dog vaccination procedure"
results = semantic_search(query)
print("\nTop search results:")
for r in results:
    print("-", r["title"])

# Simulate feedback
refresh_articles()