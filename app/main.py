import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

from dotenv import load_dotenv
load_dotenv()

            

# footer="""
#     <style>
#         .footer {
#             position: fixed;
#             left: 0;
#             bottom: 0;
#             width: 100%;
#             background-color: transparent;
#             color: white;
#             text-align: center;
#         }
#     </style>
#     <div class="footer">
#     <p>&copy;2025 Developed by Balaji R</a></p>
#     </div>
# """




def main(llm, portfolio):
    st.title("❄️ Cold Email Generator")
    st.markdown("Enter the URL of a job posting, company, or profile page to generate a personalized cold email.")
    # st.markdown(footer,unsafe_allow_html=True)

    url_input = st.text_input("🌐 Enter a URL:", value="", placeholder="https://example.com/job-posting")
    submit_button = st.button("🚀 Generate Email")

    if submit_button:
        if not url_input.strip():
            st.warning("Please enter a valid URL.")
            return

        with st.spinner("Loading and analyzing content..."):
            try:
                # st.write("🔍 Loading content from URL...")
                loader = WebBaseLoader([url_input])
                loaded_docs = loader.load()

                if not loaded_docs:
                    st.error("No content loaded from the URL. Please check the URL and try again.")
                    return

                page_content = loaded_docs.pop().page_content
                # st.write(f"✅ Loaded content length: {len(page_content)} characters")

                cleaned_text = clean_text(page_content)
                # st.write(f"✅ Cleaned content length: {len(cleaned_text)} characters")

                # st.write("💼 Extracting job postings from content...")
                jobs = llm.extract_jobs(cleaned_text)
                # st.write(f"📝 Number of jobs extracted: {len(jobs)}")
                # st.write(jobs)

                if not jobs:
                    st.info("No job information found at the provided URL.")
                    return

                for idx, job in enumerate(jobs, start=1):
                    # st.write(f"🔹 Processing job #{idx}: Role = {job.get('role', 'N/A')}")
                    skills = job.get('skills', [])

                    if not isinstance(skills, list):
                        st.warning(f"Expected 'skills' to be a list, got {type(skills)}. Skipping this job.")
                        continue
                    
                    # Initialize relevant_links before the if-else block
                    relevant_links = []
                    
                    if not skills:
                        st.info(f"No skills found for job #{idx}. Continuing without portfolio links.")
                        relevant_links = []
                    else:
                        # st.write(f"Skills for job #{idx}: {skills}")
                        relevant_metadata = portfolio.query_links(skills)
                        # st.write(f"🔗 Portfolio query returned {len(relevant_metadata)} results")
                        # st.write(relevant_metadata)
                        
                        relevant_links = []
                        seen_links = set()
                        for group in relevant_metadata:
                            for item in group:
                                if isinstance(item, dict) and 'links' in item:
                                    link = item['links']
                                    if link not in seen_links:
                                        relevant_links.append(link)
                                        seen_links.add(link)
                    
                    # Generate email
                    # st.write("✉️ Generating cold email...")
                    email = llm.write_email(job, relevant_links)

                    st.markdown(f"### ✉️ Generated Cold Email #{idx}")
                    

                    st.markdown("---")
                    st.markdown(email)
                    st.markdown("---")
                    
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(
        layout="centered",
        page_title="Cold Email Generator",
        page_icon="❄️"
    )
    chain = Chain()
    portfolio = Portfolio()
    # st.write("📂 Loading portfolio...")
    portfolio.load_portfolio()
    # st.write("✅ Portfolio loaded.")
    main(chain, portfolio)