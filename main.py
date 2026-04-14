#!/usr/bin/env python3
"""OCR application with support for input.png file."""

import sys
import os
from pathlib import Path
import cv2
import easyocr
from PIL import Image
import logging
from utils.pdf_processor import PDFProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRProcessor:
    """OCR processor using EasyOCR."""
    
    def __init__(self, lang: list = ['ru', 'en'], gpu: bool = False):
        self.lang = lang
        self.gpu = gpu
        logger.info("Initializing EasyOCR...")
        try:
            self.reader = easyocr.Reader(lang, gpu=gpu)
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
        
        # Initialize PDF processor
        try:
            self.pdf_processor = PDFProcessor()
            self.pdf_support = True
        except Exception as e:
            logger.warning(f"PDF support not available: {e}")
            self.pdf_support = False
    
    
    
        def process_image(self, image_path: str) -> str:
        """Process image and extract text."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Processing image: {image_path}")
        
        try:
            results = self.reader.readtext(image_path)
            text_lines = [text for (bbox, text, conf) in results]
            result = '\n'.join(text_lines)
            logger.info(f"OCR completed successfully. Found {len(text_lines)} text blocks")
            return result.strip()
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    def process_default_input(self) -> str:
        """Process default input.png file."""
        default_path = Path("input.png")
        if not default_path.exists():
            raise FileNotFoundError("input.png not found in current directory")
        return self.process_image(str(default_path))
    
    def process_pdf(self, pdf_path: str, page: int = None) -> str:
        """Process PDF file and extract text.
        
        Args:
            pdf_path: Path to PDF file
            page: Specific page number (1-indexed), or None for all pages
        
        Returns:
            Extracted text
        """
        if not self.pdf_support:
            raise RuntimeError("PDF support not available. Install pdf2image and poppler.")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            if page:
                # Process single page
                image_path = self.pdf_processor.pdf_page_to_image(pdf_path, page)
                result = self.process_image(image_path)
                # Clean up temp file
                if os.path.exists(image_path):
                    os.remove(image_path)
                return result
            else:
                # Process all pages
                image_paths = self.pdf_processor.pdf_to_images(pdf_path)
                results = []
                
                for i, image_path in enumerate(image_paths, start=1):
                    logger.info(f"Processing page {i}/{len(image_paths)}")
                    text = self.process_image(image_path)
                    results.append(f"=== Page {i} ===\n{text}")
                    # Clean up temp file
                    if os.path.exists(image_path):
                        os.remove(image_path)
                
                return "\n\n".join(results)
        
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise

def main():
    """Main entry point."""
    processor = OCRProcessor(lang='eng+rus')
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # Check if PDF
        if file_path.lower().endswith('.pdf'):
            if not processor.pdf_support:
                print("\nERROR: PDF support not available!")
                print("Install required packages: pip install pdf2image")
                print("See POPPLER_INSTALL.md for poppler installation.\n")
                sys.exit(1)
            
            try:
                # Check for page argument
                page = None
                if len(sys.argv) > 2:
                    try:
                        page = int(sys.argv[2])
                    except ValueError:
                        print("Invalid page number")
                        sys.exit(1)
                
                result = processor.process_pdf(file_path, page)
                print("\n=== OCR Result (PDF) ===")
                print(result)
                print("========================\n")
            except Exception as e:
                logger.error(f"Error: {e}")
                sys.exit(1)
        else:
            # Process as image
            try:
                result = processor.process_image(file_path)
                print("\n=== OCR Result ===")
                print(result)
                print("==================\n")
            except Exception as e:
                logger.error(f"Error: {e}")
                sys.exit(1)
    else:
        try:
            result = processor.process_default_input()
            print("\n=== OCR Result (input.png) ===")
            print(result)
            print("==============================\n")
        except FileNotFoundError:
            print("Usage: python main.py [file_path] [page_number]")
            print("  file_path: Path to image or PDF file")
            print("  page_number: (Optional) Specific PDF page to process")
            print("\nOr place an 'input.png' file in the current directory")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()