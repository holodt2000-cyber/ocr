@echo off
chcp 65001 >nul
echo ============================================================
echo   OCR Web Editor - Запуск
echo ============================================================
echo.
echo Запуск сервера...
echo Браузер откроется автоматически через 3 секунды
echo.
start /B timeout /t 3 /nobreak >nul
start http://localhost:5000
python web_app.py
pause
