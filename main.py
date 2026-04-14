#!/usr/bin/env python3
"""OCR application with support for input.png file."""

import sys
import os
from pathlib import Path
import cv2
import pytesseract
from PIL import Image
import logging
from utils.pdf_processor import PDFProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Auto-detect Tesseract path on Windows
if os.name == 'nt':  # Windows
    tesseract_paths = [
        os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'),
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tessdata_dir = os.path.join(os.path.dirname(path), 'tessdata')
            os.environ['TESSDATA_PREFIX'] = tessdata_dir
            logger.info(f"Tesseract found at: {path}")
            logger.info(f"TESSDATA_PREFIX set to: {tessdata_dir}")
            break

class OCRProcessor:
    """OCR processor using Tesseract."""
    
    def __init__(self, config: str = r'--oem 3 --psm 6', lang: str = 'eng'):
        self.config = config
        self.lang = lang
        self._check_tesseract()
        
        # Initialize PDF processor
        try:
            self.pdf_processor = PDFProcessor()
            self.pdf_support = True
        except Exception as e:
            logger.warning(f"PDF support not available: {e}")
            self.pdf_support = False
    
    def _check_tesseract(self):
        """Check if Tesseract is available."""
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            error_msg = (
                "\n" + "="*60 + "\n"
                "ERROR: Tesseract OCR is not installed or not in PATH!\n"
                "="*60 + "\n"
                "Please install Tesseract OCR:\n"
                "  - Windows: See INSTALL.md for detailed instructions\n"
                "  - macOS: brew install tesseract\n"
                "  - Linux: sudo apt-get install tesseract-ocr\n\n"
                "After installation, restart your terminal/command prompt.\n"
                "For detailed instructions, see: INSTALL.md\n"
                "="*60
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def process_image(self, image_path: str) -> str:
        """Process image and extract text."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Processing image: {image_path}")
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            result = pytesseract.image_to_string(img, lang=self.lang, config=self.config)
            logger.info("OCR completed successfully")
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