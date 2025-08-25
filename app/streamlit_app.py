import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from backend.api import refresh_articles, update_index_with_feedback
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


for item in kb_response.get("results", []):
    st.write("Title:", item.get("title", "Unknown"))
    st.write("Summary:", item.get("summary", "Unknown"))
    st.write("Key Entities:", item.get("key_entities", "Unknown"))
    st.write("Category:", item.get("category", "Unknown"))
    st.write("Last Updated:", item.get("last_updated", "Unknown"))
    st.write("---") 


#create a thumbs up and thumbs down button for feedback  
if st.button("👍 Helpful"):
    st.write("Thank you for your feedback!")
    update_index_with_feedback(user_prompt, kb_response.get("id"), "helpful")

if st.button("👎 Not Helpful"):
    st.write("Thank you for your feedback!")
    update_index_with_feedback(user_prompt, kb_response.get("id"), "not_helpful")

outdated_articles = [item for item in kb_response.get("results", []) if item.get("last_updated") == "unknown"]
if outdated_articles:
    st.warning(f"Warning: {len(outdated_articles)} articles have unknown last updated dates.")

    if st.button("AI Retraining Button"):     
        st.write("Refreshing articles...")
    refresh_articles()
