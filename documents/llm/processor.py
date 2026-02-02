from langchain_core.prompts import ChatPromptTemplate
from .import get_llm
from .schema import DocumentExtraction


EXTRACTION_PROMPT = """You are a document extraction expert. Analyze this document and extract structured information.

Document text:
{text}

Instructions:
1. document_type: Classify as one of: driver_license, passport, invoice, insurance_card, certificate, contract, id_card, other

2. extracted_fields: Extract key fields as a dictionary (names, numbers, dates as strings, amounts)

3. expiry_date: Find ANY expiration/expiry/valid until date. Convert to ISO format YYYY-MM-DD.
   - "03/15/2027" → "2027-03-15"
   - "March 15, 2027" → "2027-03-15"
   - "Exp: 12/25" → "2025-12-31"
   Return null ONLY if no expiration date exists.

4. activation_date: Find ANY issue/start/activation date. Convert to ISO format YYYY-MM-DD.
   Return null ONLY if no such date exists.

5. summary: One sentence describing this document.

6. confidence: 0.0-1.0 based on extraction quality.

IMPORTANT: Always convert dates to ISO format (YYYY-MM-DD). Do not return null for dates that exist in the document.
"""

class LLMProcessor:
    """ Processes extrcated text through LLM. """

    def __init__(self):
        self.llm = get_llm()
        self.structured_llm = self.llm.with_structured_output(DocumentExtraction)
        self.prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)

    def process(self, text:str) -> DocumentExtraction:
        """ Processes text and return structured extraction
        
        Args : Extracted text from docs

        Return : Document Extraction with all fields
        """
        messages = self.prompt.format_messages(text=text)
        result = self.structured_llm.invoke(messages)
        return result

