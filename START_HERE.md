# 🚀 Быстрый старт OCR проекта

## 📋 Что нужно сделать перед запуском

### 1. Установить Tesseract OCR

**Windows:**
1. Скачайте: https://github.com/UB-Mannheim/tesseract/wiki
2. Установите (запомните путь)
3. Скачайте языковые файлы:
   - Английский: https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
   - Русский: https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata
4. Поместите файлы в: `C:\Users\[ваше_имя]\AppData\Local\Programs\Tesseract-OCR\tessdata\`

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-rus
```

### 2. Установить Python зависимости

```bash
pip install -r requirements.txt
```

### 3. Проверить установку

```bash
python check_installation.py
```

Должно показать: `[SUCCESS] All dependencies are installed correctly!`

## 🎯 Как использовать

### Вариант 1: Интерактивный лаунчер (рекомендуется)

```bash
python run.py
```

Выберите нужный инструмент из меню.

### Вариант 2: Интерактивный GUI редактор

```bash
python interactive_editor.py
```

**Возможности:**
- 📁 Открыть изображение
- 🔍 Запустить OCR
- ✏️ Редактировать распознанный текст
- ➕ Добавлять новые метки
- 🗑️ Удалять текст
- 💾 Сохранять результат

### Вариант 3: Командная строка

**Базовое OCR:**
```bash
python main.py input.png
```

**OCR с позициями:**
```bash
python ocr_with_positions.py input.png all
```

**Редактирование текста:**
```bash
# Заменить
python edit_text_on_image.py input.png replace "старый" "новый"

# Удалить
python edit_text_on_image.py input.png remove "текст"

# Выделить
python edit_text_on_image.py input.png highlight "текст" yellow
```

## 📁 Структура проекта

```
ocr/
├── run.py                    # 🚀 Главный лаунчер
├── interactive_editor.py     # 🖼️ GUI редактор
├── main.py                   # 📝 Базовое OCR
├── ocr_with_positions.py     # 📍 OCR с координатами
├── edit_text_on_image.py     # ✏️ Редактирование
├── check_installation.py     # ✅ Проверка
├── download_tessdata.py      # 📥 Загрузка языков
└── requirements.txt          # 📦 Зависимости
```

## 🆘 Проблемы?

### Tesseract не найден

1. Проверьте установку: `tesseract --version`
2. Если не работает, скачайте языковые файлы вручную (см. выше)
3. Подробная инструкция: `MANUAL_SETUP.md`

### Ошибка импорта

```bash
pip install -r requirements.txt --upgrade
```

### Плохое качество распознавания

- Используйте четкие изображения
- Увеличьте разрешение
- Попробуйте разные режимы PSM

## 📚 Документация

- `README.md` - Полная документация
- `QUICKSTART.md` - Быстрый старт
- `INSTALL.md` - Детальная установка
- `EXAMPLES.md` - Примеры кода
- `MANUAL_SETUP.md` - Ручная настройка

## 🎉 Готово!

Теперь запустите:
```bash
python run.py
```

И выберите нужный инструмент!