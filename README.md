# OCR Text Recognition

Простое приложение для распознавания текста с изображений с использованием Tesseract OCR.

## Установка

### Быстрая установка

1. **Установите Tesseract OCR** (см. подробную инструкцию в [INSTALL.md](INSTALL.md)):
   - **Windows**: Скачайте установщик с [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) и добавьте в PATH
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

2. **Установите Python зависимости**:
```bash
pip install -r requirements.txt
```

⚠️ **Важно**: После установки Tesseract перезапустите командную строку/терминал!

📖 **Подробная инструкция**: См. [INSTALL.md](INSTALL.md) для детальных шагов установки

### Проверка установки

После установки всех зависимостей запустите:
```bash
python check_installation.py
```

Этот скрипт проверит все необходимые компоненты и сообщит о проблемах.

## Использование

### Вариант 1: Обработка input.png
Просто запустите программу без аргументов, и она автоматически обработает файл `input.png` в текущей директории:
```bash
python main.py
```

### Вариант 2: Обработка конкретного файла
Укажите путь к изображению:
```bash
python main.py path/to/your/image.jpg
```

## Поддерживаемые форматы
- PNG
- JPG/JPEG
- BMP
- TIFF
- GIF

## Структура проекта
```
ocr/
├── main.py              # Основной файл приложения
├── requirements.txt     # Python зависимости
├── README.md           # Документация
├── .gitignore          # Игнорируемые файлы
└── input.png           # Файл для обработки (не в репозитории)
```

## Примеры

```python
from main import OCRProcessor

# Создать процессор
processor = OCRProcessor()

# Обработать изображение
text = processor.process_image('document.png')
print(text)
```

## Требования
- Python 3.7+
- Tesseract OCR
- OpenCV
- Pytesseract
- Pillow

## Лицензия
MIT