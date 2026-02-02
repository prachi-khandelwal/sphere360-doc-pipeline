from langchain_core.prompts import ChatPromptTemplate
from .import get_llm
from .schema import DocumentExtraction


EXTRACTION_PROMPT = """ 

Analyze the following document text and extract information.

Document text:
{text}

Extract:
1. document_type: What kind of document is this? (e.g., driver_license, invoice, insurance_card, certificate, contract, passport, other)

2. extracted_fields: Key information from the document (names, numbers, amounts, etc.)

3. expiry_date: If there's an expiry/expiration date, return in ISO format (YYYY-MM-DD). If only month/year given (e.g., 12/2025), assume last day of month. Return null if none found.

4. activation_date: If there's an issue/activation/start date, return in ISO format. Return null if none found.

5. summary: One sentence describing this document.

6. confidence: How confident are you in this extraction? (0.0 to 1.0)
   - 1.0: Very clear document, all fields found
   - 0.7-0.9: Most fields found, some uncertainty
   - 0.4-0.6: Partial extraction, unclear document
   - 0.1-0.3: Poor quality, guessing
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

