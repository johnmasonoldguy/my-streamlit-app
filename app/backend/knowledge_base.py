# Example backend logic for querying a knowledge base
from app.backend.api import etl_pipeline
import os
kb_api_url = os.environ['KB_API_URL'] 
kb_api_key = os.environ['KB_API_KEY']

def query_knowledge_base(prompt: str) -> str:
    final_data = etl_pipeline(kb_api_url, kb_api_key)
    return f"Knowledge base response to: {final_data}"
