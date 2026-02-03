from docx import Document
from .base import BaseLoader, ExtractionResult


class WordLoader(BaseLoader):
    """Loader for Word documents (.docx)"""
    
    SUPPORTED_EXTENSIONS = ['.docx']

    def supports(self, file_path: str) -> bool:
        return any(file_path.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)

    def extract(self, file_path: str) -> ExtractionResult:
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            if not text.strip():
                return ExtractionResult(text="", confidence=0.0, error="Empty document")
            
            return ExtractionResult(text=text, confidence=1.0)
        except Exception as e:
            return ExtractionResult(text="", confidence=0.0, error=str(e))
