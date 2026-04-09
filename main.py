#!/usr/bin/env python3
"""
OCR project using Chandra library from GitHub.
Install: pip install -r requirements.txt
Usage: python main.py path_to_image.jpg
"""

import sys
import cv2
from PIL import Image
try:
    from chandra import OCR  # Assuming chandra pip package
except ImportError:
    print("Install chandra: pip install chandra")
    sys.exit(1)

def ocr_image(image_path):
    img = Image.open(image_path)
    ocr = OCR()
    result = ocr.run(img)
    print(result.text)
    return result.text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_path>")
        sys.exit(1)
    ocr_image(sys.argv[1])
