from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from app import config

class Chain:
    def __init__(self, model_name=None):
        self.llm = ChatGroq(
            model=model_name or config.DEFAULT_MODEL,
            temperature=0,
            groq_api_key=config.GROQ_API_KEY
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}

            ### INSTRUCTION:
            The text above is scraped from a careers page. 
            Extract all job postings and return them as a list of JSON objects.
            Each object MUST have the following keys: 'role', 'experience', 'description', and 'skills'.
            
            If no job postings are found, return an empty list [].
            
            ### VALID JSON (NO PREAMBLE):
            """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_text})
        
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Failed to parse jobs from the provided context. The content might be too large or malformed.")
            
        return res if isinstance(res, list) else [res]

    def write_email(self, job_data, links, sender_info=None):
        sender_info = sender_info or {
            "name": config.DEFAULT_SENDER_NAME,
            "role": config.DEFAULT_SENDER_ROLE,
            "company": config.DEFAULT_COMPANY_NAME,
            "description": config.DEFAULT_COMPANY_DESCRIPTION
        }

        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are **{sender_name}**, a {sender_role} at **{company_name}** — {company_description}
            
            Your task is to write a **cold email** to a potential client about the role described above. The email should:

            **Content Requirements:**
            - Start with a **subject line** that clearly states the offer or value
            - Open with a friendly paragraph relating to their hiring or project needs
            - Casually explain how {company_name} has solved similar challenges
            - Add the most relevant ones from the following links to show our portfolio {link_list}
            - Highlight 2-3 relevant past projects or portfolios using bullet points
            - Be persuasive without being salesy — think: "we get your world, and we can help"
            - End with a soft CTA like suggesting a quick call or sending case studies
            - Keep the tone friendly, confident, and focused on the client's benefit
            - Don't keep it long.

            **Formatting Requirements:**
            - Format the email in a **business-casual style** with proper structure
            - Use clear paragraph breaks (double line breaks between paragraphs)
            - Structure with: Subject line, greeting, introduction, body paragraphs, call-to-action, signature
            - Use bullet points for project lists and key highlights
            - Ensure proper spacing between all sections
            - Keep paragraphs short and readable

            **Signature Formatting:** use this in the response
            Best regards,

            {sender_name}
            {sender_role}
            {company_name}

            You're not writing to "sell" — you're starting a conversation and showing how {company_name} can add real value.
            Provide placeholders like [Name] for personalization if specific recipient name is unknown.

            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job_data),
            "link_list": links,
            "sender_name": sender_info["name"],
            "sender_role": sender_info["role"],
            "company_name": sender_info["company"],
            "company_description": sender_info["description"]
        })
        return res.content
