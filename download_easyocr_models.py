#!/usr/bin/env python3
"""Download EasyOCR models manually."""

import os
import urllib.request
from pathlib import Path

# EasyOCR model URLs (GitHub releases)
MODELS = {
    'craft_mlt_25k.pth': 'https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/craft_mlt_25k.zip',
    'latin_g2.pth': 'https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/latin_g2.zip',
    'cyrillic_g2.pth': 'https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/cyrillic_g2.zip'
}

# Get EasyOCR model directory
home = Path.home()
model_dir = home / '.EasyOCR' / 'model'
model_dir.mkdir(parents=True, exist_ok=True)

print("Директория моделей:", model_dir)
print("\nПопытка загрузки моделей EasyOCR...")
print("Это может занять несколько минут...\n")

for model_name, url in MODELS.items():
    model_path = model_dir / model_name
    
    if model_path.exists():
        print(f"✓ {model_name} уже загружен")
        continue
    
    print(f"Загрузка {model_name}...")
    try:
        # Try direct download
        urllib.request.urlretrieve(url, str(model_path))
        print(f"✓ {model_name} загружен успешно")
    except Exception as e:
        print(f"✗ Ошибка загрузки {model_name}: {e}")
        print(f"  Попробуйте скачать вручную: {url}")

print("\n" + "="*60)
print("Альтернативный способ:")
print("="*60)
print("1. Используйте VPN или прокси")
print("2. Скачайте модели вручную с:")
print("   https://github.com/JaidedAI/EasyOCR/releases")
print(f"3. Поместите их в: {model_dir}")
print("="*60)
