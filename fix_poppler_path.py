import re

with open("web_app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add poppler path configuration
if "poppler_path =" not in code:
    code = code.replace(
        "try:\n    from pdf2image import convert_from_path\n    PDF_SUPPORT = True\nexcept ImportError:\n    PDF_SUPPORT = False",
        """try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
    # Set poppler path for Windows
    import platform
    if platform.system() == 'Windows':
        poppler_path = r'C:\\Program Files\\poppler\\Library\\bin'
    else:
        poppler_path = None
except ImportError:
    PDF_SUPPORT = False
    poppler_path = None"""
    )

# Update convert_from_path calls to use poppler_path
code = code.replace(
    "images = convert_from_path(filepath)",
    "images = convert_from_path(filepath, poppler_path=poppler_path)"
)

with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Poppler path configured!")
