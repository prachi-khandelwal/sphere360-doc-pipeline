from PIL import Image, ImageEnhance, ImageOps
from documents.loaders.base import BaseLoader, ExtractionResult
import pytesseract


class ImageLoader(BaseLoader):
    """ Image loader class to extract text from Images using OCR """
    SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']

    def supports(self, file_path: str) -> bool:
        "Checks if file is an image "
        lower_path = file_path.lower()
        return any(lower_path.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR - handles both light and dark backgrounds."""
        # Convert to grayscale
        img = image.convert('L')

        # Check if image is predominantly dark (light text on dark bg)
        avg_brightness = sum(img.getdata()) / (img.width * img.height)
        if avg_brightness < 128:
            img = ImageOps.invert(img)

        # Enhance contrast
        img = ImageEnhance.Contrast(img).enhance(2.0)

        # Enhance sharpness
        img = ImageEnhance.Sharpness(img).enhance(1.5)

        return img

    def extract(self, file_path: str) -> ExtractionResult:
        """ Extract text from image"""

        try:
            image = Image.open(file_path)

            # Try preprocessed image first for better results
            processed = self._preprocess_image(image)
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed, config=custom_config)

            # Fallback to raw image if preprocessing yielded nothing
            if not text.strip():
                text = pytesseract.image_to_string(image)

            if not text.strip():
                return ExtractionResult(
                    text="",
                    confidence=0.0,
                    error="No text found in image"
                )

            return ExtractionResult(
                text=text,
                confidence=0.85
            )

        except Exception as e:
            return ExtractionResult(
                text="",
                confidence=0.0,
                error=str(e)
            )