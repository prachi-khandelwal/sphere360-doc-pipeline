from .base import BaseLoader, ExtractionResult
from .pdf_loader import PDFLoader
from .image_loader import ImageLoader
from .text_loader import TextLoader



class LoaderFactory:
    """ Factory class to get the right loader for a file """

    _loaders = [
        PDFLoader(),
        ImageLoader(),
        TextLoader(),
    ]

    @classmethod
    def get_loader(cls, file_path:str) -> BaseLoader:
        """ Get appropriate file Loader 
        
        Args : file path

        Returns : Loader that can handle file
        """

        for loader in cls._loaders:
            if loader.supports(file_path):
                return loader

        raise ValueError(f"No loader found for : {file_path}")


    @classmethod
    def supported_extensions(cls) -> list:
        """Get all supported file extensions."""
        extensions = []
        for loader in cls._loaders:
            extensions.extend(loader.SUPPORTED_EXTENSIONS)
        return extensions




