#!/usr/bin/env python3
"""Test PDF processing functionality."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_processor import PDFProcessor

def test_pdf_support():
    """Test if PDF support is available."""
    print("="*60)
    print("Testing PDF Support")
    print("="*60)
    
    try:
        pdf_processor = PDFProcessor()
        print("[OK] PDF support is available")
        print(f"  DPI: {pdf_processor.dpi}")
        print(f"  Poppler path: {pdf_processor.poppler_path or 'Auto-detected'}")
        return True
    except ImportError as e:
        print("[ERROR] PDF support not available")
        print(f"  Error: {e}")
        print("\nInstall required packages:")
        print("  pip install pdf2image")
        return False
    except Exception as e:
        print("[ERROR] PDF support error")
        print(f"  Error: {e}")
        return False

def test_pdf_conversion(pdf_path):
    """Test PDF to image conversion."""
    print("\n" + "="*60)
    print(f"Testing PDF Conversion: {pdf_path}")
    print("="*60)
    
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return False
    
    try:
        pdf_processor = PDFProcessor()
        
        # Get page count
        page_count = pdf_processor.get_pdf_page_count(pdf_path)
        print(f"[OK] PDF has {page_count} page(s)")
        
        # Convert first page
        print("\nConverting first page...")
        image_path = pdf_processor.pdf_page_to_image(pdf_path, 1)
        print(f"[OK] Converted to: {image_path}")
        
        # Check if file exists
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path) / 1024  # KB
            print(f"  File size: {file_size:.2f} KB")
            
            # Clean up
            os.remove(image_path)
            print("  Cleaned up temporary file")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        return False

def main():
    """Main test function."""
    print("\n" + "="*60)
    print("PDF Functionality Test")
    print("="*60 + "\n")
    
    # Test 1: Check PDF support
    if not test_pdf_support():
        print("\n" + "="*60)
        print("RESULT: PDF support not available")
        print("="*60)
        print("\nSee POPPLER_INSTALL.md for installation instructions.")
        sys.exit(1)
    
    # Test 2: Convert PDF if provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        success = test_pdf_conversion(pdf_path)
        
        print("\n" + "="*60)
        if success:
            print("RESULT: All tests passed [OK]")
        else:
            print("RESULT: Some tests failed [ERROR]")
        print("="*60 + "\n")
        
        sys.exit(0 if success else 1)
    else:
        print("\n" + "="*60)
        print("RESULT: Basic PDF support available [OK]")
        print("="*60)
        print("\nTo test PDF conversion, run:")
        print("  python scripts/test_pdf.py <path_to_pdf>")
        print("\nExample:")
        print("  python scripts/test_pdf.py document.pdf")
        print()

if __name__ == "__main__":
    main()