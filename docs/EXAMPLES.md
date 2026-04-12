# Примеры использования

## Базовое использование

### Пример 1: Обработка input.png

```python
from main import OCRProcessor

processor = OCRProcessor()
text = processor.process_default_input()
print(text)
```

### Пример 2: Обработка конкретного файла

```python
from main import OCRProcessor

processor = OCRProcessor()
text = processor.process_image('document.jpg')
print(text)
```

## Продвинутое использование

### Пример 3: Кастомная конфигурация Tesseract

```python
from main import OCRProcessor

# PSM 3 = Fully automatic page segmentation
processor = OCRProcessor(config='--oem 3 --psm 3')
text = processor.process_image('page.png')
print(text)
```

### Пример 4: Пакетная обработка

```python
from main import OCRProcessor
import os
from pathlib import Path

processor = OCRProcessor()
image_folder = Path('images')

for image_file in image_folder.glob('*.png'):
    try:
        text = processor.process_image(str(image_file))
        print(f"\n{image_file.name}:")
        print(text)
        print("-" * 50)
    except Exception as e:
        print(f"Error processing {image_file}: {e}")
```

### Пример 5: Сохранение результатов в файл

```python
from main import OCRProcessor
from pathlib import Path

processor = OCRProcessor()
image_path = 'document.png'
output_path = 'output.txt'

try:
    text = processor.process_image(image_path)
    
    # Сохранить в файл
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Text saved to {output_path}")
except Exception as e:
    print(f"Error: {e}")
```

### Пример 6: Обработка с предварительной обработкой изображения

```python
import cv2
import numpy as np
from main import OCRProcessor

def preprocess_image(image_path):
    """Улучшить изображение перед OCR."""
    # Загрузить изображение
    img = cv2.imread(image_path)
    
    # Конвертировать в grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Применить пороговую обработку
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Убрать шум
    denoised = cv2.fastNlMeansDenoising(thresh)
    
    # Сохранить обработанное изображение
    processed_path = 'processed_temp.png'
    cv2.imwrite(processed_path, denoised)
    
    return processed_path

# Использование
processor = OCRProcessor()
original_image = 'noisy_document.png'

# Предобработка
processed_image = preprocess_image(original_image)

# OCR
text = processor.process_image(processed_image)
print(text)

# Удалить временный файл
import os
os.remove(processed_image)
```

### Пример 7: Распознавание с несколькими языками

```python
import pytesseract
import cv2

def ocr_multilang(image_path, languages='eng+rus'):
    """OCR с поддержкой нескольких языков."""
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img, lang=languages)
    return text.strip()

# Использование
text = ocr_multilang('mixed_language.png', 'eng+rus')
print(text)
```

### Пример 8: Получение координат текста

```python
import pytesseract
import cv2
from PIL import Image

def get_text_boxes(image_path):
    """Получить координаты текстовых блоков."""
    img = cv2.imread(image_path)
    
    # Получить данные о расположении текста
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    boxes = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Confidence > 60%
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            text = data['text'][i]
            boxes.append({
                'text': text,
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'confidence': data['conf'][i]
            })
    
    return boxes

# Использование
boxes = get_text_boxes('document.png')
for box in boxes:
    print(f"Text: {box['text']}, Position: ({box['x']}, {box['y']}), Confidence: {box['confidence']}%")
```

## Режимы PSM (Page Segmentation Mode)

```python
from main import OCRProcessor

# PSM 0 = Orientation and script detection (OSD) only
processor = OCRProcessor(config='--psm 0')

# PSM 3 = Fully automatic page segmentation (default)
processor = OCRProcessor(config='--psm 3')

# PSM 6 = Assume a single uniform block of text
processor = OCRProcessor(config='--psm 6')

# PSM 7 = Treat the image as a single text line
processor = OCRProcessor(config='--psm 7')

# PSM 8 = Treat the image as a single word
processor = OCRProcessor(config='--psm 8')

# PSM 10 = Treat the image as a single character
processor = OCRProcessor(config='--psm 10')
```

## Обработка ошибок

```python
from main import OCRProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processor = OCRProcessor()

try:
    text = processor.process_image('document.png')
    print(text)
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
except ValueError as e:
    logger.error(f"Invalid image: {e}")
except RuntimeError as e:
    logger.error(f"Tesseract error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Интеграция с другими библиотеками

### С pandas для табличных данных

```python
import pandas as pd
from main import OCRProcessor

processor = OCRProcessor()
text = processor.process_image('table.png')

# Парсинг табличных данных (простой пример)
lines = text.strip().split('\n')
data = [line.split() for line in lines if line.strip()]

df = pd.DataFrame(data[1:], columns=data[0])
print(df)
```

### С Flask для веб-приложения

```python
from flask import Flask, request, jsonify
from main import OCRProcessor
import os

app = Flask(__name__)
processor = OCRProcessor()

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    temp_path = 'temp_upload.png'
    file.save(temp_path)
    
    try:
        text = processor.process_image(temp_path)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True)
```