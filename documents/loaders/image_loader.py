from PIL import Image
from documents.loaders.base import BaseLoader, ExtractionResult
import pytesseract


class ImageLoader(BaseLoader):
    """ Image loader class to extract text from Images using OCR """
    SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']

    def supports(self, file_path: str) -> bool:
        "Checks if file is an image "
        lower_path = file_path.lower()
        return any(lower_path.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)

    def extract(self, file_path:str) -> ExtractionResult:
        """ Extract text from image"""

        try:
            image = Image.open(file_path)
            text = image.pytesseract.image_to_string(image)
        
            if not text.strip():
                return ExtractionResult(
                    text = "",
                    confidence= 0.0,
                    error = "No text found in image"
                )

            return ExtractionResult(
                text = text,
                confidence= 1.0
            )

        except Exception as e:
            return ExtractionResult(
                text = text,
                confidence= 0.0,
                erorr = str(e)
            )