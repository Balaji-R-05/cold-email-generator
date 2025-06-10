import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )


    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT From website
        {page_data}
        ### INSTRUCTION:
        Your scraped text is from career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing following keys:
        'role', 'experience', 'description' and 'skills'.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE)
        """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]
    

    def write_email(self, jobs, links):
        prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}

        ### INSTRUCTION:
        You are **Ravi Sharma**, a Business Consultant at **Techspire Solutions** — a forward-thinking tech consulting firm focused on helping companies build smarter, faster, and more scalable digital systems.
        Techspire specializes in delivering tailored AI and software solutions that simplify operations, accelerate product development, and cut costs — whether it's through automation, platform engineering, or custom development.
        
        Your task is to write a **cold email** to a potential client about the role described above. The email should:

        **Content Requirements:**
        - Start with a **subject line** that clearly states the offer or value
        - Open with a friendly paragraph relating to their hiring or project needs
        - Casually explain how Techspire has solved similar challenges
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

        Balaji R
        Business Consultant
        Techspire Solutions

        You're not writing to "sell" — you're starting a conversation and showing how Techspire can add real value.
        You are **Balaji R**, Business Consultant at **Techspire Solutions**.

        ### EMAIL (NO PREAMBLE):
        """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke(
        {"job_description": str(jobs), "link_list": links}
        )
        return res.content