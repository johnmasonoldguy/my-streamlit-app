from pathlib import Path

import re
def extract_body_html(html_string):
    match = re.search(r'<body[^>]*>(.*?)</body>', html_string, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return html_string
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from backend.api import refresh_articles, update_index_with_feedback
from backend.knowledge_base import query_knowledge_base

"""
## Unified Veterinary Knowledge Assistant
"""

def main():
    # Display HTML and DITA content for each file
    html_folder = Path("./app/backend/html_articles")
    dita_folder = Path("./app/backend/dita_articles")
    html_files = list(html_folder.glob("*.html"))
    dita_files = list(dita_folder.glob("*.dita"))

    if html_files:
        st.header("HTML and DITA Articles")
        for html_file in html_files:
            html_content = html_file.read_text(encoding="utf-8")
            st.subheader(f"HTML: {html_file.stem}")
            st.markdown(extract_body_html(html_content), unsafe_allow_html=True)

            # Find matching DITA file (e.g., input.html -> input_full.dita)
            dita_match = None
            for dita_file in dita_files:
                if dita_file.stem == f"{html_file.stem}_full":
                    dita_match = dita_file
                    break
            if dita_match:
                dita_content = dita_match.read_text(encoding="utf-8")
                st.markdown(f"**DITA XML for {dita_match.name}:**")
                st.code(dita_content, language="xml")
                # Feedback buttons for DITA file
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"👍 Helpful (DITA) {dita_match.stem}", key=f"dita_helpful_{dita_match.stem}"):
                        st.success("Thank you for your feedback!")
                        update_index_with_feedback("", html_file.stem, "helpful")
                with col2:
                    if st.button(f"👎 Not Helpful (DITA) {dita_match.stem}", key=f"dita_not_helpful_{dita_match.stem}"):
                        st.info("Thank you for your feedback!")
                        update_index_with_feedback("", html_file.stem, "not_helpful")

if __name__ == "__main__":
    main()
