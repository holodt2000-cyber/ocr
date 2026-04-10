import urllib.request
import ssl
import os

# Disable SSL verification (for corporate networks)
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata"
output = os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tessdata\eng.traineddata")

print(f"Downloading from: {url}")
print(f"Saving to: {output}")

try:
    urllib.request.urlretrieve(url, output)
    print("[OK] Downloaded successfully!")
except Exception as e:
    print(f"[ERROR] {e}")
    print("\nPlease download manually:")
    print(f"1. Open in browser: {url}")
    print(f"2. Save file to: {output}")