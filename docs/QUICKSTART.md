# Быстрый старт

## За 3 шага к работающему OCR

### Шаг 1: Установите Tesseract OCR

**Windows:**
1. Скачайте: https://github.com/UB-Mannheim/tesseract/wiki
2. Установите (запомните путь установки)
3. Добавьте в PATH или перезапустите терминал

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Шаг 2: Установите Python зависимости

```bash
pip install -r requirements.txt
```

### Шаг 3: Проверьте установку

```bash
python check_installation.py
```

Если все OK, переходите к использованию!

## Использование

### Вариант 1: Автоматическая обработка input.png

1. Поместите изображение с именем `input.png` в папку проекта
2. Запустите:
```bash
python main.py
```

### Вариант 2: Обработка конкретного файла

```bash
python main.py path/to/your/image.jpg
```

### Вариант 3: Создать тестовое изображение

```bash
python example_usage.py
```

Это создаст `input.png` с примером текста и обработает его.

## Решение проблем

### "Tesseract OCR not found in PATH"

1. Убедитесь, что Tesseract установлен:
   ```bash
   tesseract --version
   ```

2. Если команда не найдена:
   - **Windows**: Добавьте `C:\Program Files\Tesseract-OCR` в PATH
   - **macOS/Linux**: Переустановите через пакетный менеджер

3. Перезапустите терминал после изменения PATH

### Плохое качество распознавания

- Используйте четкие изображения с высоким разрешением
- Убедитесь, что текст контрастный
- Попробуйте разные режимы PSM (см. документацию)

## Дополнительная информация

- Полная документация: [README.md](README.md)
- Детальная установка: [INSTALL.md](INSTALL.md)
- История изменений: [CHANGELOG.md](CHANGELOG.md)

## Поддержка

Если возникли проблемы:
1. Запустите `python check_installation.py`
2. Проверьте [INSTALL.md](INSTALL.md)
3. Убедитесь, что все зависимости установлены