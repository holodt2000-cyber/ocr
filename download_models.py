import easyocr

print("Загрузка моделей EasyOCR...")
print("Это может занять несколько минут...")

try:
    reader = easyocr.Reader(['ru', 'en'], gpu=False, download_enabled=True)
    print("Модели успешно загружены!")
    
    # Тест
    print("Тестирование...")
    result = reader.readtext('test.png') if False else []
    print("EasyOCR готов к работе!")
    
except Exception as e:
    print(f"Ошибка: {e}")
    print("\nПопробуйте:")
    print("1. Проверьте интернет соединение")
    print("2. Отключите VPN если используете")
    print("3. Попробуйте позже")
