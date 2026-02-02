from codecs import utf_16_encode
from .base import ExtractionResult, BaseLoader

class TextLoader(BaseLoader):
    "Loader for plain text"

    SUPPORTED_EXTENSIONS = ['.txt', '.text']
    def support(self, file_path: str) -> bool:
        "Checks for correct file"
        return any(file_path.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)

    def extract(self, file_path: str) -> ExtractionResult:
        """ Extracts data from text plain files """

        try:
            with open(file_path, 'r', encoding = 'utf_16') as f:
                text = f.read()

            if not text.strip():
                return ExtractionResult(
                    text="",
                    confidence=0.0,
                    error="File is empty"
                )

            return ExtractionResult(
                text=text,
                confidence=1.0
            )

        except Exception as e:
            return ExtractionResult(
                text="",
                confidence=0.0,
                error=str(e)
            )

            
