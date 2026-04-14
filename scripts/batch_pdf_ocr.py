#!/usr/bin/env python3
"""Batch process multiple PDF files with OCR."""

import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import OCRProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_pdf_folder(folder_path: str, output_folder: str = None):
    """Process all PDF files in a folder.
    
    Args:
        folder_path: Path to folder containing PDF files
        output_folder: Path to save text files (default: same as input)
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        logger.error(f"Folder not found: {folder_path}")
        return
    
    # Find all PDF files
    pdf_files = list(folder.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in: {folder_path}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Setup output folder
    if output_folder:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = folder
    
    # Initialize OCR processor
    processor = OCRProcessor(lang='eng+rus')
    
    if not processor.pdf_support:
        logger.error("PDF support not available!")
        logger.error("Install pdf2image and poppler. See POPPLER_INSTALL.md")
        return
    
    # Process each PDF
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(pdf_files, start=1):
        logger.info(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            # Process PDF
            text = processor.process_pdf(str(pdf_file))
            
            # Save to text file
            output_file = output_path / f"{pdf_file.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"✓ Saved to: {output_file}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"✗ Failed to process {pdf_file.name}: {e}")
            error_count += 1
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Batch processing complete!")
    logger.info(f"Success: {success_count}")
    logger.info(f"Errors: {error_count}")
    logger.info(f"{'='*60}\n")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python batch_pdf_ocr.py <folder_path> [output_folder]")
        print("\nExample:")
        print("  python batch_pdf_ocr.py ./pdfs")
        print("  python batch_pdf_ocr.py ./pdfs ./output")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_pdf_folder(folder_path, output_folder)

if __name__ == "__main__":
    main()