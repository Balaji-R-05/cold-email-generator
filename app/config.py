import os
from dotenv import load_dotenv

load_dotenv(override=True)

# LLM Settings
DEFAULT_MODEL = "llama-3.3-70b-versatile"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Default Personalization
DEFAULT_SENDER_NAME = "Ravi Sharma"
DEFAULT_SENDER_ROLE = "Business Consultant"
DEFAULT_COMPANY_NAME = "Techspire Solutions"
DEFAULT_COMPANY_DESCRIPTION = (
    "a forward-thinking tech consulting firm focused on helping companies "
    "build smarter, faster, and more scalable digital systems. Techspire specializes "
    "in delivering tailored AI and software solutions that simplify operations, "
    "accelerate product development, and cut costs."
)

# Portfolio Settings
PORTFOLIO_CSV = "my_portfolio.csv"
VECTORSTORE_PATH = "vectorstore"