# Example backend logic for querying a knowledge base
import os
import json
from unittest import result

from backend.api import get_embedding, semantic_search

# kb_api_url = os.environ['KB_API_URL']
# kb_api_key = os.environ['KB_API_KEY']

def query_knowledge_base(user_prompt) -> list:
    results = semantic_search(user_prompt)
    print(f"KB Query Results: {results}")
    return results  