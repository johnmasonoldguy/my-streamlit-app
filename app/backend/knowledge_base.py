# Example backend logic for querying a knowledge base
import os
import json

from backend.api import get_embedding

# kb_api_url = os.environ['KB_API_URL']
# kb_api_key = os.environ['KB_API_KEY']

def query_knowledge_base(user_prompt) -> dict:
   results = get_embedding(user_prompt)
   return results   