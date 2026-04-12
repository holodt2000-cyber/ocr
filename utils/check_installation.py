#!/usr/bin/env python3
"""Check if all dependencies are installed correctly."""

import sys

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 7:
        print("[OK] Python version is compatible")
        return True
    else:
        print("[ERROR] Python 3.7+ required")
        return False

def check_opencv():
    """Check OpenCV installation."""
    try:
        import cv2
        print(f"[OK] OpenCV installed (version: {cv2.__version__})")
        return True
    except ImportError:
        print("[ERROR] OpenCV not installed. Run: pip install opencv-python")
        return False

def check_pillow():
    """Check Pillow installation."""
    try:
        from PIL import Image
        import PIL
        print(f"[OK] Pillow installed (version: {PIL.__version__})")
        return True
    except ImportError:
        print("[ERROR] Pillow not installed. Run: pip install pillow")
        return False

def check_numpy():
    """Check NumPy installation."""
    try:
        import numpy as np
        print(f"[OK] NumPy installed (version: {np.__version__})")
        return True
    except ImportError:
        print("[ERROR] NumPy not installed. Run: pip install numpy")
        return False

def check_pytesseract():
    """Check pytesseract installation."""
    try:
        import pytesseract
        print("[OK] pytesseract installed")
        return True
    except ImportError:
        print("[ERROR] pytesseract not installed. Run: pip install pytesseract")
        return False

def check_tesseract_binary():
    """Check if Tesseract OCR binary is available."""
    try:
        import pytesseract
        import os
        
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
                    print(f"[INFO] Tesseract found at: {path}")
                    break
        
        version = pytesseract.get_tesseract_version()
        print(f"[OK] Tesseract OCR installed (version: {version})")
        return True
    except Exception as e:
        print("[ERROR] Tesseract OCR not found")
        print("        Please install Tesseract OCR:")
        print("        - Windows: See INSTALL.md")
        print("        - macOS: brew install tesseract")
        print("        - Linux: sudo apt-get install tesseract-ocr")
        return False

def main():
    """Run all checks."""
    print("="*60)
    print("Checking OCR Project Dependencies")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("OpenCV", check_opencv),
        ("Pillow", check_pillow),
        ("NumPy", check_numpy),
        ("pytesseract", check_pytesseract),
        ("Tesseract OCR Binary", check_tesseract_binary),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        results.append(check_func())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    print("="*60)
    
    if all(results):
        print("\n[SUCCESS] All dependencies are installed correctly!")
        print("You can now run: python main.py")
        return 0
    else:
        print("\n[WARNING] Some dependencies are missing.")
        print("Please install missing dependencies and try again.")
        print("See INSTALL.md for detailed instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())