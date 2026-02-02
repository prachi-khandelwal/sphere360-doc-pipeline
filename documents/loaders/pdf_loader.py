import fitz
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
from .base import BaseLoader, ExtractionResult

class PDFLoader(BaseLoader):
    """
    Loader for pdf docs - supports both text and scanned PDFs
    """
    SUPPORTED_EXTENSIONS = ['.pdf']

    def supports(self, file_path: str) -> bool:
        """ Check if file is a PDF or not """
        return file_path.lower().endswith('.pdf')

    def _extract_text_direct(self, doc) -> str:
        """Extract text directly from PDF"""
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()

    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Auto-crop to content (remove white margins)
        # Convert to grayscale first for getbbox
        gray_for_crop = img.convert('L')
        
        # Find content by looking for non-near-white pixels
        # Invert and use point to create mask of dark pixels
        threshold = 250
        mask = gray_for_crop.point(lambda x: 255 if x < threshold else 0)
        bbox = mask.getbbox()
        
        if bbox:
            # Add small padding
            padding = 20
            left = max(0, bbox[0] - padding)
            top = max(0, bbox[1] - padding)
            right = min(img.width, bbox[2] + padding)
            bottom = min(img.height, bbox[3] + padding)
            img = img.crop((left, top, right, bottom))
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        return img

    def _extract_text_ocr(self, doc) -> str:
        """Extract text using OCR for scanned PDFs"""
        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page to image at 300 DPI for better OCR
            mat = fitz.Matrix(300/72, 300/72)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            # Preprocess for better OCR
            img = self._preprocess_image(img)
            
            # Save debug image (optional - comment out in production)
            # img.save(f"debug_page_{page_num}.png")
            
            # Run OCR with English + Hindi support and custom config
            custom_config = r'--oem 3 --psm 6'
            page_text = pytesseract.image_to_string(img, lang='eng+hin', config=custom_config)
            text += page_text + "\n"
        
        return text.strip()

    def extract(self, file_path: str) -> ExtractionResult:
        """ Extract Text from PDF - uses OCR if needed """
        try:
            doc = fitz.open(file_path)
            
            # First try direct text extraction
            text = self._extract_text_direct(doc)
            
            # If no text found, try OCR
            if not text:
                text = self._extract_text_ocr(doc)
                confidence = 0.85  # OCR is slightly less reliable
            else:
                confidence = 1.0
            
            doc.close()

            if not text:
                return ExtractionResult(
                    text="",
                    confidence=0.0,
                    error="No text extracted even with OCR"
                )

            return ExtractionResult(
                text=text,
                confidence=confidence
            )

        except Exception as e:
            return ExtractionResult(
                text="",
                confidence=0.0,
                error=str(e)
            )
        