import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from backend.api import refresh_articles, update_index_with_feedback
from backend.knowledge_base import query_knowledge_base

"""
## Unified Veterinary Knowledge Assistant
"""

user_prompt = st.text_input("Enter your question or prompt:")
kb_response = None

if user_prompt:
    kb_response = query_knowledge_base(user_prompt)
    st.write("Knowledge Base Response:")

    if kb_response and isinstance(kb_response, (list, tuple)):
        for idx, item in enumerate(kb_response):
            if isinstance(item, dict):
                with st.expander(f"{item.get('title', f'Result {idx+1}')}", expanded=False):
                    for key, value in item.items():
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                    # Feedback buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"👍 Helpful {idx}", key=f"helpful_{idx}"):
                            st.success("Thank you for your feedback!")
                            update_index_with_feedback(user_prompt, item.get("id"), "helpful")
                    with col2:
                        if st.button(f"👎 Not Helpful {idx}", key=f"not_helpful_{idx}"):
                            st.success("Thank you for your feedback!")
                            update_index_with_feedback(user_prompt, item.get("id"), "not_helpful")
            else:
                st.write("-", str(item))
        # Check for outdated articles
        outdated_articles = [item for item in kb_response if isinstance(item, dict) and item.get("last_updated", "").lower() == "unknown"]
        if outdated_articles:
            st.warning(f"Warning: {len(outdated_articles)} articles have unknown last updated dates.")
            if st.button("AI Retraining Button"):
                st.write("Refreshing articles...")
                refresh_articles()
    else:
        st.write("No results found or unexpected response format.")
