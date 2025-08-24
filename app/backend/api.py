import openai
import requests
import json

import os
OpenAI = os.environ['OPENAI_KEY']
kb_api_url = os.environ['KB_API_URL'] 
kb_api_key = os.environ['KB_API_KEY']

# 1. Configure OpenAI
openai.api_key = OpenAI

# 2. Sample function to fetch content from a KB (Neo/Animana API)
def fetch_kb_content(api_url, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_url, headers=headers)
    return response.json()  # assume JSON response with 'articles'

# 3. AI-driven content cleaning & structuring
def ai_clean_and_structure(article_text):
    prompt = f"""
    You are an ETL agent. Analyze the following knowledge base content, 
    clean it, and convert it into a structured JSON format with:
    - title
    - summary
    - key_entities
    - category
    - last_updated
    
    Content:
    {article_text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    # Parse AI output into JSON
    structured_data = response.choices[0].message.content
    return json.loads(structured_data)

# 4. Example ETL loop
def etl_pipeline(kb_api_url, kb_api_key):
    content = fetch_kb_content(kb_api_url, kb_api_key)
    structured_articles = []
    
    for article in content.get("articles", []):
        structured = ai_clean_and_structure(article.get("body", ""))
        structured_articles.append(structured)
    
    return structured_articles

# 5. Run pipeline
final_data = etl_pipeline(kb_api_url, kb_api_key)

# 6. Save to JSON or push to enterprise content platform
with open("structured_kb_data.json", "w") as f:
    json.dump(final_data, f, indent=2)

print("ETL pipeline completed. Data ready for ingestion.")