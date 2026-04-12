# Установка Poppler для работы с PDF

## Windows

1. Скачайте Poppler:
   https://github.com/oschwartz10612/poppler-windows/releases/latest
   
2. Скачайте файл: Release-XX.XX.X-X.zip

3. Распакуйте в: C:\Program Files\poppler

4. Добавьте в PATH:
   - Откройте "Система" → "Дополнительные параметры системы"
   - "Переменные среды"
   - В "Path" добавьте: C:\Program Files\poppler\Library\bin
   - Перезапустите командную строку

5. Проверьте:
   ```
   pdftoppm -v
   ```

## Альтернатива (без установки)

Если не хотите устанавливать Poppler, просто используйте изображения (PNG, JPG).
PDF поддержка опциональна.

## После установки

Перезапустите START.bat и попробуйте загрузить PDF файл.
