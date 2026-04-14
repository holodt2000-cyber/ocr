# Руководство по работе с PDF

## Установка

### 1. Установите зависимости Python
```bash
pip install -r requirements.txt
```

### 2. Установите Poppler (для PDF)

**Windows:**
- Скачайте: https://github.com/oschwartz10612/poppler-windows/releases/latest
- Распакуйте в `C:\Program Files\poppler`
- Добавьте в PATH: `C:\Program Files\poppler\Library\bin`
- Перезапустите командную строку

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt-get install poppler-utils
```

Подробнее: см. `POPPLER_INSTALL.md`

## Использование

### Веб-интерфейс

1. Запустите приложение:
   ```bash
   python web_app.py
   # или на Windows: START.bat
   ```

2. Откройте браузер: http://localhost:5000

3. Загрузите PDF файл через кнопку "📁 Открыть файл"

4. Навигация по страницам:
   - Используйте кнопки "◀ Назад" и "Вперед ▶"
   - Текущая страница отображается в центре

5. Обработка:
   - Нажмите "🔍 Распознать текст" для OCR текущей страницы
   - Редактируйте распознанный текст
   - Перетаскивайте текстовые блоки мышью
   - Добавляйте новые метки кликом

6. Сохранение:
   - Нажмите "💾 Сохранить" для экспорта изображения с текстом

### Командная строка

#### Обработать весь PDF
```bash
python main.py document.pdf
```

Вывод:
```
=== Page 1 ===
[текст первой страницы]

=== Page 2 ===
[текст второй страницы]
...
```

#### Обработать конкретную страницу
```bash
python main.py document.pdf 3
```

Обработает только страницу 3.

#### Пакетная обработка

Обработать все PDF в папке:
```bash
python scripts/batch_pdf_ocr.py ./pdfs
```

С указанием папки для результатов:
```bash
python scripts/batch_pdf_ocr.py ./pdfs ./output
```

Создаст текстовые файлы (.txt) для каждого PDF.

## Программное использование

```python
from main import OCRProcessor

# Инициализация
processor = OCRProcessor(lang='eng+rus')

# Проверка поддержки PDF
if not processor.pdf_support:
    print("PDF support not available")
    exit(1)

# Обработать весь PDF
text = processor.process_pdf('document.pdf')
print(text)

# Обработать конкретную страницу
text = processor.process_pdf('document.pdf', page=3)
print(text)
```

### Использование PDFProcessor напрямую

```python
from utils.pdf_processor import PDFProcessor

# Инициализация
pdf_proc = PDFProcessor(dpi=300)

# Конвертировать PDF в изображения
image_paths = pdf_proc.pdf_to_images('document.pdf', 'output_folder')

# Получить количество страниц
page_count = pdf_proc.get_pdf_page_count('document.pdf')

# Конвертировать одну страницу
image_path = pdf_proc.pdf_page_to_image('document.pdf', page_number=1)
```

## Настройки

### Качество конвертации

В `utils/pdf_processor.py` можно изменить DPI:

```python
pdf_processor = PDFProcessor(dpi=300)  # По умолчанию 300
# Выше DPI = лучше качество, но медленнее и больше файлы
```

### Языки OCR

В `main.py` и `web_app.py`:

```python
processor = OCRProcessor(lang='eng+rus')  # Английский + Русский
# или
processor = OCRProcessor(lang='eng')      # Только английский
```

## Устранение проблем

### "PDF support not available"

1. Проверьте установку pdf2image:
   ```bash
   pip install pdf2image
   ```

2. Проверьте установку Poppler:
   ```bash
   pdftoppm -v
   ```

3. На Windows убедитесь, что Poppler в PATH

### "Failed to convert PDF"

1. Проверьте, что PDF файл не поврежден
2. Попробуйте открыть PDF в другой программе
3. Проверьте права доступа к файлу

### Медленная обработка

1. Уменьшите DPI (например, до 200)
2. Обрабатывайте по одной странице за раз
3. Используйте более мощный компьютер

## Ограничения

- PDF должны содержать растровые изображения (не векторный текст)
- Большие PDF могут требовать много памяти
- Качество OCR зависит от качества исходного PDF
- Защищенные паролем PDF не поддерживаются

## Советы

1. **Качество**: Используйте PDF с высоким разрешением (300+ DPI)
2. **Производительность**: Обрабатывайте страницы по отдельности для больших документов
3. **Точность**: Проверяйте и редактируйте результаты OCR
4. **Пакетная обработка**: Используйте `batch_pdf_ocr.py` для множества файлов

## Примеры использования

### Сканированные документы
```bash
python main.py scanned_document.pdf
```

### Многостраничные отчеты
```bash
# Обработать каждую страницу отдельно
for i in {1..10}; do
    python main.py report.pdf $i > page_$i.txt
done
```

### Архив документов
```bash
python scripts/batch_pdf_ocr.py ./archive ./extracted_text
```