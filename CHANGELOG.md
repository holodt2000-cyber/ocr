# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2026-04-10

### Added
- Comprehensive installation guide (INSTALL.md)
- Dependency checker script (check_installation.py)
- Quick start guide (QUICKSTART.md)
- Extensive examples documentation (EXAMPLES.md)
- MIT License file
- Better error messages when Tesseract is not installed
- Fallback checks for missing dependencies

### Changed
- Improved error handling with helpful installation instructions
- Enhanced README with installation verification steps
- Fixed encoding issues in example scripts

### Fixed
- Unicode encoding errors in Windows console output
- Better detection of missing Tesseract installation

## [2.0.0] - 2026-04-10

### Added
- Автоматическая обработка файла `input.png` при запуске без аргументов
- Класс `OCRProcessor` для лучшей организации кода
- Логирование процесса обработки
- Обработка ошибок и валидация входных данных
- Unit тесты (`test_ocr.py`)
- Полная документация в README.md
- .gitignore для исключения ненужных файлов

### Changed
- Рефакторинг кода для улучшения читаемости
- Улучшенная обработка ошибок
- Более информативные сообщения об ошибках

### Fixed
- Проверка существования файла перед обработкой
- Корректная обработка различных форматов изображений

## [1.0.0] - Initial Release
- Базовая функциональность OCR