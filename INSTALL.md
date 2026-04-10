# Инструкция по установке Tesseract OCR

## Windows

### Шаг 1: Скачать Tesseract
1. Перейдите на страницу: https://github.com/UB-Mannheim/tesseract/wiki
2. Скачайте последнюю версию установщика (например, `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

### Шаг 2: Установить Tesseract
1. Запустите скачанный установщик
2. **ВАЖНО**: Запомните путь установки (по умолчанию: `C:\Program Files\Tesseract-OCR`)
3. Завершите установку

### Шаг 3: Добавить в PATH

#### Вариант A: Автоматически (рекомендуется)
Во время установки отметьте галочку "Add to PATH"

#### Вариант B: Вручную
1. Откройте "Система" → "Дополнительные параметры системы"
2. Нажмите "Переменные среды"
3. В разделе "Системные переменные" найдите `Path`
4. Нажмите "Изменить"
5. Добавьте путь к Tesseract (например: `C:\Program Files\Tesseract-OCR`)
6. Нажмите "ОК" во всех окнах
7. **Перезапустите командную строку/терминал**

### Шаг 4: Проверить установку
Откройте новое окно командной строки и выполните:
```cmd
tesseract --version
```

Вы должны увидеть версию Tesseract.

### Шаг 5: Установить Python зависимости
```cmd
pip install -r requirements.txt
```

## macOS

```bash
# Установить Homebrew (если еще не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установить Tesseract
brew install tesseract

# Установить Python зависимости
pip install -r requirements.txt
```

## Linux (Ubuntu/Debian)

```bash
# Обновить пакеты
sudo apt-get update

# Установить Tesseract
sudo apt-get install tesseract-ocr

# Установить дополнительные языки (опционально)
sudo apt-get install tesseract-ocr-rus  # Русский
sudo apt-get install tesseract-ocr-eng  # Английский

# Установить Python зависимости
pip install -r requirements.txt
```

## Проверка работы

После установки запустите:
```bash
python example_usage.py
```

Если все установлено правильно, вы увидите распознанный текст с созданного изображения.

## Решение проблем

### Ошибка: "tesseract is not installed or it's not in your PATH"
- Убедитесь, что Tesseract установлен
- Проверьте, что путь к Tesseract добавлен в PATH
- Перезапустите командную строку/терминал
- Попробуйте указать путь явно в коде:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Плохое качество распознавания
- Используйте изображения с высоким разрешением
- Убедитесь, что текст четкий и контрастный
- Попробуйте разные PSM режимы (см. документацию Tesseract)

### Не распознается русский текст
- Установите языковой пакет для русского языка
- Укажите язык при вызове: `pytesseract.image_to_string(img, lang='rus')`