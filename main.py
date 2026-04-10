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

class OCRProcessor:
    """OCR processor using Tesseract."""
    
    def __init__(self, config: str = r'--oem 3 --psm 6'):
        self.config = config
    
    def process_image(self, image_path: str) -> str:
        """Process image and extract text."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Processing image: {image_path}")
        
        try:
            # Read image using OpenCV
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Perform OCR
            result = pytesseract.image_to_string(img, config=self.config)
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
    processor = OCRProcessor()
    
    # Check if image path provided as argument
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
        # Try to process input.png by default
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
