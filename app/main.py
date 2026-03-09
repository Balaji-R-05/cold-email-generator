import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import config

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
        model_name = st.selectbox("LLM Model", options=["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"], index=0)

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

    if submit_button:
        if not url_input.strip():
            st.warning("Please enter a valid URL.")
            return

        with st.spinner("Analyzing job posting..."):
            try:
                # Initialize logic
                llm = Chain(model_name=model_name)
                portfolio = Portfolio()
                portfolio.load_portfolio()

                # Load and clean content
                loader = WebBaseLoader([url_input])
                loaded_docs = loader.load()
                if not loaded_docs:
                    st.error("No content found at the URL.")
                    return

                page_content = loaded_docs[0].page_content
                cleaned_text = clean_text(page_content)

                # Extract jobs
                jobs = llm.extract_jobs(cleaned_text)

                if not jobs:
                    st.info("No job postings detected on this page.")
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
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()