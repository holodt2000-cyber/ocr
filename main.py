#!/usr/bin/env python3
"""OCR application with support for input.png file."""

import sys
import os
from pathlib import Path
import cv2
import pytesseract
from PIL import Image
import logging

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

def main():
    """Main entry point."""
    processor = OCRProcessor(lang='eng+rus')
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        try:
            result = processor.process_image(image_path)
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
            print("Usage: python main.py [image_path]")
            print("Or place an 'input.png' file in the current directory")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()