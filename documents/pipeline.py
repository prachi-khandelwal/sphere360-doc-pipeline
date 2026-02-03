from dataclasses import dataclass, asdict
from typing import List, Optional, Any, Dict
import os

import documents

from .loaders import LoaderFactory, ExtractionResult
from .llm.processor import LLMProcessor
from .llm.schema import DocumentExtraction


@dataclass
class DocumentResult:
    """Final result for single document."""
    source: str
    source_type: str
    document_type: str
    extracted_fields: Dict[str, Any]
    expiry_date: Optional[str]
    activation_date: Optional[str]
    confidence: float
    summary: str
    error: Optional[str] = None



@dataclass
class BatchResult:
    """ Result for batch Processing """
    documents: List[DocumentResult]
    total: int
    successful: int
    failed: int



class Pipeline:
    """ Main pipeline  connects LLM and Loaders"""

    def __init__(self):
        self.processor = LLMProcessor()

    def _get_source_type(self, file_path: str) -> str:
        """ Determine source type from file extension """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return 'image'
        elif ext == '.docx':
            return 'word'
        else:
            return 'text'

    def process_single(self, file_path:str) -> DocumentResult:
        """ Processes Single doc only
        
        Args : File path

        Returns : Document Results for single doc
        """

        source = os.path.basename(file_path)  #filename
        source_type = self._get_source_type(file_path)

        # S1 : Get Loader , Extract it
        try:
            loader = LoaderFactory.get_loader(file_path)
            extraction = loader.extract(file_path)

        except Exception as e:
            return DocumentResult(
                    source = source,
                    source_type = source_type,
                    document_type = "unknown",
                    extracted_fields = {},
                    expiry_date = None,
                    activation_date = None,
                    confidence = 0.0,
                    summary = "",
                    error = f"Extraction failed {str(e)}",
            )

        #S2 : Check if Extraction is valid / succedded or not
        if extraction.error or not extraction.text.strip():
            return DocumentResult(
                    source = source,
                    source_type = source_type,
                    document_type = "unknown",
                    extracted_fields = {},
                    expiry_date = None,
                    activation_date = None,
                    confidence = 0.0,
                    summary = "",
                    error = extraction.error or "No text extracted"
            )

        #         # DEBUG: Print extracted text to verify OCR quality
        # print(f"\n--- OCR EXTRACTED TEXT for {source} ---")
        # print(extraction.text)
        # print(f"--- END OCR TEXT (confidence: {extraction.confidence}) ---\n")

        # S3 : Process with LLM (with chunking support for large docs)
        try:
            llm_result = self.processor.process_chunked(extraction.text)
        except Exception as e:
            return DocumentResult(
                source=source,
                source_type=source_type,
                document_type="unknown",
                extracted_fields={},
                expiry_date=None,
                activation_date=None,
                confidence=0.0,
                summary="",
                error=f"LLM Processing Failed: {str(e)}",
            )
        
        # S4 : Combine confidences and return
        # Final confidence = Loader confidence × LLM confidence
        # This ensures poor OCR (0.5) + good LLM (0.9) = 0.45 (correctly low)
        # And good text (1.0) + good LLM (0.9) = 0.9 (correctly high)
        combined_confidence = extraction.confidence * llm_result.confidence
        
        return DocumentResult(
            source=source,
            source_type=source_type,
            document_type=llm_result.document_type,
            extracted_fields=llm_result.extracted_fields,
            expiry_date=llm_result.expiry_date,
            activation_date=llm_result.activation_date,
            confidence=round(combined_confidence, 2),
            summary=llm_result.summary,
        )

    def process_batch(self, file_paths: List[str]) -> BatchResult:
        """  Process multiple documents"""
        results = []
        for file_path in file_paths:
            result = self.process_single(file_path)
            results.append(result)

        successful = sum(1 for r in results if r.error is None)
        failed = len(results) - successful
        
        return BatchResult(
            documents=results,
            total=len(results),
            successful=successful,
            failed=failed
        )













        
        