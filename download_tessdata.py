#!/usr/bin/env python3
"""Download Tesseract language data files."""

import os
import urllib.request
import sys

def download_language_data(lang='eng'):
    """Download Tesseract language data."""
    
    # Find Tesseract installation
    tesseract_paths = [
        os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR'),
        r'C:\Program Files\Tesseract-OCR',
        r'C:\Program Files (x86)\Tesseract-OCR'
    ]
    
    tessdata_dir = None
    for base_path in tesseract_paths:
        potential_dir = os.path.join(base_path, 'tessdata')
        if os.path.exists(potential_dir):
            tessdata_dir = potential_dir
            break
    
    if not tessdata_dir:
        print("ERROR: Tesseract installation not found!")
        print("Please install Tesseract OCR first.")
        return False
    
    print(f"Found tessdata directory: {tessdata_dir}")
    
    # Download language file
    url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{lang}.traineddata"
    output_file = os.path.join(tessdata_dir, f"{lang}.traineddata")
    
    if os.path.exists(output_file):
        print(f"[OK] {lang}.traineddata already exists")
        return True
    
    print(f"Downloading {lang}.traineddata...")
    try:
        urllib.request.urlretrieve(url, output_file)
        print(f"[OK] Downloaded {lang}.traineddata successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download: {e}")
        print(f"\nPlease download manually from:")
        print(f"  {url}")
        print(f"And save to:")
        print(f"  {output_file}")
        return False

def main():
    """Main entry point."""
    print("="*60)
    print("Tesseract Language Data Downloader")
    print("="*60 + "\n")
    
    # Download English by default
    languages = ['eng']
    
    # Check if user specified languages
    if len(sys.argv) > 1:
        languages = sys.argv[1:]
    
    success_count = 0
    for lang in languages:
        print(f"\nProcessing language: {lang}")
        if download_language_data(lang):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"Downloaded {success_count}/{len(languages)} language files")
    print("="*60)
    
    if success_count == len(languages):
        print("\n[SUCCESS] All language files downloaded!")
        print("You can now run: python main.py")
        return 0
    else:
        print("\n[WARNING] Some downloads failed.")
        print("Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())