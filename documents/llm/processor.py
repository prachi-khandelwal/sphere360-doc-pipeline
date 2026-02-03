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
        """ Merge results from ALL chunks - combining extracted fields.
        
        Strategy:
        1. Merge extracted_fields from ALL chunks (no data loss)
        2. Take dates from chunk with highest confidence that found them
        3. Use most common document_type across chunks
        4. Combine summaries or take the best one
        5. Average confidence scores
        """
        from collections import Counter
        
        # 1. Merge ALL extracted_fields from every chunk
        merged_fields = {}
        for result in results:
            if result.extracted_fields:
                for key, value in result.extracted_fields.items():
                    # If key exists, keep the more complete value
                    if key not in merged_fields:
                        merged_fields[key] = value
                    elif value and (not merged_fields[key] or len(str(value)) > len(str(merged_fields[key]))):
                        merged_fields[key] = value
        
        # 2. Get expiry_date from most confident chunk that has it
        expiry_candidates = [r for r in results if r.expiry_date]
        expiry_date = None
        if expiry_candidates:
            best_expiry = max(expiry_candidates, key=lambda r: r.confidence)
            expiry_date = best_expiry.expiry_date
        
        # 3. Get activation_date from most confident chunk that has it
        activation_candidates = [r for r in results if r.activation_date]
        activation_date = None
        if activation_candidates:
            best_activation = max(activation_candidates, key=lambda r: r.confidence)
            activation_date = best_activation.activation_date
        
        # 4. Most common document_type (voting)
        doc_types = [r.document_type for r in results if r.document_type and r.document_type != 'other']
        if doc_types:
            document_type = Counter(doc_types).most_common(1)[0][0]
        else:
            document_type = results[0].document_type
        
        # 5. Best summary (longest non-empty, or from highest confidence)
        summaries = [(r.summary, r.confidence) for r in results if r.summary and r.summary.strip()]
        if summaries:
            summary = max(summaries, key=lambda x: (len(x[0]), x[1]))[0]
        else:
            summary = ""
        
        # 6. Average confidence (weighted by whether chunk found useful data)
        weighted_confidences = []
        for r in results:
            weight = 1.0
            if r.expiry_date:
                weight += 0.5
            if r.activation_date:
                weight += 0.3
            if r.extracted_fields:
                weight += 0.2 * min(len(r.extracted_fields), 5) / 5
            weighted_confidences.append(r.confidence * weight)
        
        avg_confidence = sum(weighted_confidences) / sum(
            1 + (0.5 if r.expiry_date else 0) + (0.3 if r.activation_date else 0) + 
            (0.2 * min(len(r.extracted_fields) if r.extracted_fields else 0, 5) / 5)
            for r in results
        )
        
        print(f"    [Merge] Combined {len(results)} chunks: {len(merged_fields)} fields, "
              f"expiry={expiry_date}, activation={activation_date}")
        
        return DocumentExtraction(
            document_type=document_type,
            extracted_fields=merged_fields,
            expiry_date=expiry_date,
            activation_date=activation_date,
            summary=summary,
            confidence=min(avg_confidence, 1.0)
        )

