from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional




@dataclass
class ExtractionResult:
    "Holds result of extraction"
    text: str
    confidence: float
    error: Optional[str] = None


class BaseLoader(ABC):
    "Abstarct base class for document loaders"

    @abstractmethod
    def extract(self, file_path:str) -> ExtractionResult:
        """Extract text from document

        Args: file_path

        Returns : Extraction Result with Extracted text and confidence score


        """
        pass

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """ Checks if this loader supports given file 

        Args:

        file_path : Path to check

        Return:
        True if loader can handle this file
        
         """
        pass

    