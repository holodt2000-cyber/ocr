with open("web_app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Update PDF handling with better error message
old_error = '''return jsonify({'error': f'PDF error: {str(e)}'}), 400'''
new_error = '''return jsonify({'error': 'PDF требует Poppler. Скачайте: https://github.com/oschwartz10612/poppler-windows/releases/ и добавьте в PATH'}), 400'''

code = code.replace(old_error, new_error)

with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("PDF error message updated")
