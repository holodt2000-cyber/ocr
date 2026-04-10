# Ручная настройка Tesseract (если автоматическая загрузка не работает)

## Проблема
Если вы видите ошибку:
```
Error opening data file eng.traineddata
```

Это означает, что языковые файлы Tesseract не установлены.

## Решение

### Шаг 1: Скачать языковой файл

1. Откройте в браузере: https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
2. Файл должен автоматически скачаться (размер ~25 MB)
3. Если не скачался, нажмите правой кнопкой → "Сохранить как..."

### Шаг 2: Поместить файл в правильную папку

**Для вашей системы путь:**
```
C:\Users\user\AppData\Local\Programs\Tesseract-OCR\tessdata\eng.traineddata
```

**Как найти папку:**
1. Нажмите `Win + R`
2. Введите: `%USERPROFILE%\AppData\Local\Programs\Tesseract-OCR\tessdata`
3. Нажмите Enter
4. Скопируйте скачанный файл `eng.traineddata` в эту папку

### Шаг 3: Проверить установку

Запустите:
```bash
python check_installation.py
```

Вы должны увидеть:
```
[OK] Tesseract OCR installed (version: 5.5.0...)
```

### Шаг 4: Протестировать OCR

```bash
python main.py
```

## Дополнительные языки

### Русский язык:
1. Скачать: https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata
2. Поместить в ту же папку `tessdata`
3. Использовать: `pytesseract.image_to_string(img, lang='rus')`

### Другие языки:
- Список всех языков: https://github.com/tesseract-ocr/tessdata
- Скачайте нужный `.traineddata` файл
- Поместите в папку `tessdata`

## Проверка файлов

После установки в папке `tessdata` должны быть:
```
tessdata/
├── eng.traineddata  ← Этот файл нужен!
├── configs/
├── script/
└── tessconfigs/
```

## Альтернативный способ (если браузер не работает)

1. Попросите коллегу скачать файл
2. Перенесите через USB/email
3. Поместите в папку tessdata

## Все еще не работает?

1. Убедитесь, что файл называется точно `eng.traineddata` (не `eng.traineddata.txt`)
2. Проверьте размер файла (~25 MB)
3. Перезапустите командную строку
4. Попробуйте переустановить Tesseract

## Контакты для помощи

Если проблема не решается, создайте issue с описанием:
- Версия Windows
- Путь к Tesseract
- Содержимое папки tessdata
- Полный текст ошибки