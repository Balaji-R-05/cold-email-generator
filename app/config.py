import os
from dotenv import load_dotenv

load_dotenv(override=True)

# LLM Settings
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment variables")

# Default Personalization
DEFAULT_SENDER_NAME: str = "Balaji"
DEFAULT_SENDER_ROLE: str = "Business Consultant"
DEFAULT_COMPANY_NAME: str = "NotARealCompany"

# DEFAULT_COMPANY_DESCRIPTION: str = (
#     "A forward-thinking tech consulting firm focused on helping companies "
#     "build smarter, faster, and more scalable digital systems. Techspire specializes "
#     "in delivering tailored AI and software solutions that simplify operations, "
#     "accelerate product development, and cut costs."
# )

DEFAULT_COMPANY_DESCRIPTION: str = (
    "We partner with organizations to deliver high-quality talent solutions tailored to their workforce needs. "
    "Our focus is on providing dependable professionals who align with your goals, ensuring productivity "
    "from day one. We specializes in delivering tailored AI and software solutions that simplify operations, "
    "accelerate product development, and cut costs."
)

# Portfolio Settings
PORTFOLIO_CSV: str = "my_portfolio.csv"
VECTORSTORE_PATH: str = "vectorstore"