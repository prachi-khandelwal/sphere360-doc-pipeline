from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .import get_llm
from .schema import DocumentExtraction


EXTRACTION_PROMPT = """You are a document extraction expert. Analyze this document and extract structured information.

Document text:
{text}

Instructions:
1. document_type: Classify as one of: driver_license, passport, invoice, insurance_card, certificate, contract, id_card, credit_card, other

2. extracted_fields: Extract key fields as a dictionary (names, numbers, amounts, identifiers). 
   DO NOT include expiry_date or activation_date here - those have their own dedicated fields below.

3. expiry_date: REQUIRED if any expiration date exists. Look for: "Valid Through", "Valid Thru", "Expires", "Expiry", "Exp", "Good Through", "MM/YY" format near "Valid".
   Convert to ISO format YYYY-MM-DD:
   - "09/28" or "09/2028" → "2028-09-01"
   - "09/15/2027" → "2027-09-15"
   Return null ONLY if absolutely no expiration date exists.

4. activation_date: REQUIRED if any issue/start date exists. Look for: "Issue Date", "Issued", "Start Date", "Effective Date", "Created".
   Convert to ISO format YYYY-MM-DD.
   Return null ONLY if absolutely no issue/start date exists.

5. summary: One sentence describing this document.

6. confidence: 0.0-1.0 based on extraction quality.

CRITICAL: The expiry_date and activation_date fields MUST be populated directly - do NOT put these dates only in extracted_fields.
"""

class LLMProcessor:
    """ Processes extracted text through LLM with chunking support. """

    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 200):
        self.llm = get_llm()
        self.structured_llm = self.llm.with_structured_output(DocumentExtraction)
        self.prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)
        
        # Text splitter for large documents
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def process(self, text: str) -> DocumentExtraction:
        """ Processes text and return structured extraction
        
        Args : Extracted text from docs

        Return : Document Extraction with all fields
        """
        messages = self.prompt.format_messages(text=text)
        result = self.structured_llm.invoke(messages)
        return result

    def process_chunked(self, text: str) -> DocumentExtraction:
        """ Process text with chunking for large documents.
        
        Splits text into chunks, processes each, and merges results
        by picking the best extraction.
        
        Args: text - Extracted text from document
        
        Returns: DocumentExtraction with best results
        """
        chunks = self.splitter.split_text(text)
        
        # If text fits in single chunk, process directly
        if len(chunks) <= 1:
            return self.process(text)
        
        print(f"    [Chunking] Document split into {len(chunks)} chunks")
        
        # Process each chunk
        results: List[DocumentExtraction] = []
        for i, chunk in enumerate(chunks):
            try:
                result = self.process(chunk)
                results.append(result)
                print(f"    [Chunk {i+1}/{len(chunks)}] expiry={result.expiry_date}, activation={result.activation_date}, conf={result.confidence}")
            except Exception as e:
                print(f"    [Chunk {i+1}/{len(chunks)}] Error: {e}")
                continue
        
        if not results:
            raise ValueError("All chunks failed to process")
        
        return self._merge_results(results)

    def _merge_results(self, results: List[DocumentExtraction]) -> DocumentExtraction:
        """ Merge results from multiple chunks.
        
        Strategy: Pick result with highest confidence that found dates.
        Priority: has expiry_date > has activation_date > confidence score
        """
        best = max(results, key=lambda r: (
            r.expiry_date is not None,
            r.activation_date is not None,
            r.confidence
        ))
        return best

