import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path and load environment variables before any other imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'), override=True)

import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from app.chains import Chain
from app.portfolio import Portfolio
from app.utils import clean_text
from app import config

# Fix for ChromaDB in some environments (like Docker/Linux)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

def main():
    st.set_page_config(
        layout="wide",
        page_title="Cold Email Generator",
        page_icon="❄️"
    )

    # --- Sidebar Settings ---
    st.sidebar.title("⚙️ Settings")
    
    with st.sidebar.expander("👤 Personalization", expanded=True):
        sender_name = st.text_input("Your Name", value=config.DEFAULT_SENDER_NAME)
        sender_role = st.text_input("Your Role", value=config.DEFAULT_SENDER_ROLE)
        company_name = st.text_input("Company Name", value=config.DEFAULT_COMPANY_NAME)
        company_description = st.text_area("Company Description", value=config.DEFAULT_COMPANY_DESCRIPTION, height=150)

    with st.sidebar.expander("🔑 API & Model", expanded=False):
        model_name = st.selectbox("LLM Model", options=["llama-3.3-70b-versatile"], index=0)

    st.sidebar.markdown("---")
    refresh_portfolio = st.sidebar.button("🔄 Sync Portfolio CSV")

    sender_info = {
        "name": sender_name,
        "role": sender_role,
        "company": company_name,
        "description": company_description
    }

    # --- Main UI ---
    st.title("❄️ Cold Email Generator")
    st.markdown("Generate personalized, high-conversion cold emails from job postings in seconds.")

    url_input = st.text_input("🌐 Enter Job Posting URL:", placeholder="https://careers.company.com/job/software-engineer")
    submit_button = st.button("🚀 Generate Email", disabled=not url_input)

    if refresh_portfolio:
        with st.spinner("Re-syncing portfolio..."):
            Portfolio().load_portfolio(force_rebuild=True)
        st.sidebar.success("Portfolio synced!")

    if submit_button:
        if not url_input.strip() or not (url_input.startswith("http://") or url_input.startswith("https://")):
            st.warning("Please enter a valid URL starting with http:// or https://")
            return

        with st.spinner("🔍 Analyzing job posting (this may take a few seconds)..."):
            try:
                # Initialize logic
                llm = Chain(model_name=model_name)
                portfolio = Portfolio()
                portfolio.load_portfolio()

                # Load and clean content
                loader = WebBaseLoader([url_input])
                try:
                    loaded_docs = loader.load()
                except Exception as scrape_err:
                    st.error(f"Failed to scrape the URL: {str(scrape_err)}. Some websites block automated access.")
                    return

                if not loaded_docs:
                    st.error("No content found at the URL. It might be protected or require JavaScript.")
                    return

                page_content = loaded_docs[0].page_content
                cleaned_text = clean_text(page_content)

                # Extract jobs
                jobs = llm.extract_jobs(cleaned_text)

                if not jobs:
                    st.info("No job postings detected on this page. Try copying the job description text manually if the URL is protected.")
                    return

                # Process each job
                for idx, job in enumerate(jobs, start=1):
                    role = job.get('role', 'N/A')
                    skills = job.get('skills', [])
                    
                    with st.expander(f"📋 Extracted Job #{idx}: {role}", expanded=(len(jobs) == 1)):
                        st.write(f"**Experience:** {job.get('experience', 'N/A')}")
                        st.write(f"**Skills:** {', '.join(skills) if skills else 'None detected'}")
                        st.write("**Description:**")
                        st.write(job.get('description', 'N/A'))

                    # Query portfolio
                    links = portfolio.query_links(skills) if skills else []
                    
                    # Generate email
                    email = llm.write_email(job, links, sender_info=sender_info)

                    st.markdown(f"### ✉️ Generated Cold Email for {role}")
                    st.code(email, language="markdown", wrap_lines=True)
                    st.markdown("---")
                    
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.info("Tip: If the error is related to output parsing, the job description might be too complex or the model might be overloaded.")

if __name__ == "__main__":
    main()
