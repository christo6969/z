"""
Class Detection Module
Detects school class mentions in text and PDF files
Pattern: [1-5][A-Z]{2} (e.g., 1AA, 2BC, 5XY)
"""

import re
import logging
from typing import Set, List
import PyPDF2
import io

from config import CLASS_PATTERN, MAX_PDF_SIZE_MB, PDF_TIMEOUT

logger = logging.getLogger(__name__)


class ClassDetector:
    """Detects and extracts unique class mentions from text and PDF files"""
    
    def __init__(self):
        self.pattern = re.compile(CLASS_PATTERN)
    
    def detect_classes_in_text(self, text: str) -> Set[str]:
        """
        Detect unique class mentions in text
        
        Args:
            text: Text content to search
            
        Returns:
            Set of unique class codes found
        """
        if not text:
            return set()
        
        matches = self.pattern.findall(text)
        unique_classes = set(matches)
        
        if unique_classes:
            logger.info(f"Detected classes in text: {', '.join(sorted(unique_classes))}")
        
        return unique_classes
    
    def detect_classes_in_pdf(self, pdf_content: bytes) -> Set[str]:
        """
        Extract text from PDF and detect class mentions
        Optimized for Raspberry Pi with size limits
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Set of unique class codes found
        """
        # Check PDF size
        size_mb = len(pdf_content) / (1024 * 1024)
        if size_mb > MAX_PDF_SIZE_MB:
            logger.warning(f"PDF size ({size_mb:.2f}MB) exceeds limit ({MAX_PDF_SIZE_MB}MB)")
            return set()
        
        try:
            # Use PyPDF2 for lightweight PDF parsing
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            all_classes = set()
            
            # Extract text from all pages
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Detect classes in this page
                    page_classes = self.detect_classes_in_text(text)
                    all_classes.update(page_classes)
                    
                except Exception as e:
                    logger.error(f"Error extracting text from page {page_num}: {e}")
                    continue
            
            if all_classes:
                logger.info(f"Detected classes in PDF: {', '.join(sorted(all_classes))}")
            
            return all_classes
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return set()
    
    def format_classes_output(self, classes: Set[str]) -> str:
        """
        Format detected classes for display
        
        Args:
            classes: Set of class codes
            
        Returns:
            Formatted string for display
        """
        if not classes:
            return ""
        
        sorted_classes = sorted(classes)
        return f"\n📚 Classi rilevate: {', '.join(sorted_classes)}"
    
    def process_message(self, text: str = None, pdf_content: bytes = None) -> str:
        """
        Process a message (text and/or PDF) and return formatted class detection
        
        Args:
            text: Optional text content
            pdf_content: Optional PDF content
            
        Returns:
            Formatted output with detected classes
        """
        all_classes = set()
        
        # Detect classes in text
        if text:
            all_classes.update(self.detect_classes_in_text(text))
        
        # Detect classes in PDF
        if pdf_content:
            all_classes.update(self.detect_classes_in_pdf(pdf_content))
        
        return self.format_classes_output(all_classes)


# Global instance
detector = ClassDetector()


def detect_classes(text: str = None, pdf_content: bytes = None) -> str:
    """
    Convenience function to detect classes
    
    Args:
        text: Optional text content
        pdf_content: Optional PDF content
        
    Returns:
        Formatted output with detected classes
    """
    return detector.process_message(text, pdf_content)
