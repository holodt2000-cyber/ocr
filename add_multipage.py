import re

with open("web_app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Update session data structure
code = code.replace(
    "session_data = {\n    'image_path': None,\n    'text_boxes': []\n}",
    """session_data = {
    'pages': [],  # List of page objects
    'current_page': 0,
    'total_pages': 0
}"""
)

# Update upload to handle multiple pages
old_pdf_handling = """        # Handle PDF
        if filename.lower().endswith('.pdf'):
            if PDF_SUPPORT:
                try:
                    images = convert_from_path(filepath, first_page=1, last_page=1)
                    if images:
                        img = images[0]
                        img_path = filepath.replace('.pdf', '.png')
                        img.save(img_path, 'PNG')
                        session_data['image_path'] = img_path
                        with open(img_path, 'rb') as f:
                            img_data = base64.b64encode(f.read()).decode('utf-8')
                    else:
                        return jsonify({'error': 'Failed to convert PDF'}), 400
                except Exception as e:
                    return jsonify({'error': 'PDF требует Poppler. Скачайте: https://github.com/oschwartz10612/poppler-windows/releases/ и добавьте в PATH'}), 400
            else:
                return jsonify({'error': 'PDF support not installed'}), 400
        else:
            session_data['image_path'] = filepath
            with open(filepath, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')"""

new_pdf_handling = """        # Handle PDF - convert all pages
        if filename.lower().endswith('.pdf'):
            if PDF_SUPPORT:
                try:
                    images = convert_from_path(filepath)
                    session_data['pages'] = []
                    session_data['total_pages'] = len(images)
                    session_data['current_page'] = 0
                    
                    for i, img in enumerate(images):
                        img_path = filepath.replace('.pdf', f'_page_{i+1}.png')
                        img.save(img_path, 'PNG')
                        session_data['pages'].append({
                            'image_path': img_path,
                            'text_boxes': [],
                            'show_background': True
                        })
                    
                    # Return first page
                    with open(session_data['pages'][0]['image_path'], 'rb') as f:
                        img_data = base64.b64encode(f.read()).decode('utf-8')
                    
                    return jsonify({
                        'success': True,
                        'image': img_data,
                        'filename': filename,
                        'total_pages': len(images),
                        'current_page': 1
                    })
                except Exception as e:
                    return jsonify({'error': 'PDF требует Poppler. Скачайте: https://github.com/oschwartz10612/poppler-windows/releases/ и добавьте в PATH'}), 400
            else:
                return jsonify({'error': 'PDF support not installed'}), 400
        else:
            # Single image
            session_data['pages'] = [{
                'image_path': filepath,
                'text_boxes': [],
                'show_background': True
            }]
            session_data['total_pages'] = 1
            session_data['current_page'] = 0
            
            with open(filepath, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')"""

code = code.replace(old_pdf_handling, new_pdf_handling)

with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Multi-page PDF support added!")
