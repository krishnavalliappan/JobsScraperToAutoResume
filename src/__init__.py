# src/__init__.py

# You can leave this file empty if you don't need any initialization code

# Optionally, you can import and expose specific modules or functions
from .scraper_linkedin import LinkedIn
# from .processor import DataProcessor, GPTProcessor
# from .document_generator import WordGenerator, PDFGenerator
# from .notion_integration import NotionManager

# If you want to define a version for your package
__version__ = "0.1.0"

# You can also include any initialization code here if needed
# For example, setting up logging for the entire package
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
