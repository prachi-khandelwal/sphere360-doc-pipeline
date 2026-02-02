import fitz
from .base import BaseLoader, ExtractionResult

class PDFLoader(BaseLoader):
    """
    Loader for pdf docs
    """
    SUPPORTED_EXTENSIONS = ['.pdf']

    def supports(self, file_path:str) -> bool:
        """ Check if file is a PDF or not """
        return file_path.lower().endswith('.pdf')

    def extract(self, file_path: str) -> ExtractionResult:
        """ Extract Text from PDF """
        try:
            doc = fitz.open(file_path)
            text = ""

            for page in doc:
                text += page.get_text()
            doc.close()

            if not text.strip():
                return ExtractionResult(
                    text = "",
                    confidence = 0.0,
                    error = "No text found - may be scanned pdf"

                )

            return ExtractionResult(
                text = text,
                confidence= 1.0
            )

        except Exception as e:
            return ExtractionResult(
                text = "",
                confidence = 0.0,
                error = str(e)
            )
        