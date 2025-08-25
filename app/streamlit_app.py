import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from backend.knowledge_base import query_knowledge_base

"""
# Knowledge Database!
"""

# Prompt to query the knowledge base
st.header("Query the Knowledge Base")
user_prompt = st.text_input("Enter your question or prompt:")
if user_prompt:
    kb_response = query_knowledge_base(user_prompt)
    st.write("Knowledge Base Response:", kb_response)


# for item in structured_output:
#     st.write("Title:", item.get("title", "Unknown"))
#     st.write("Summary:", item.get("summary", "Unknown"))
#     st.write("Key Entities:", item.get("key_entities", "Unknown"))
#     st.write("Category:", item.get("category", "Unknown"))
#     st.write("Last Updated:", item.get("last_updated", "Unknown"))
#     st.write("---") 
