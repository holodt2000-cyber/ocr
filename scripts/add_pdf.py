import re

with open("web_app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add PDF import
if "from pdf2image import convert_from_path" not in code:
    code = code.replace(
        "import json",
        "import json\ntry:\n    from pdf2image import convert_from_path\n    PDF_SUPPORT = True\nexcept ImportError:\n    PDF_SUPPORT = False"
    )

# Update upload function to handle PDF
old_upload = """    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        session_data['image_path'] = filepath
        session_data['text_boxes'] = []
        
        # Convert image to base64 for display
        with open(filepath, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_data,
            'filename': filename
        })"""

new_upload = """    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        session_data['text_boxes'] = []
        
        # Handle PDF
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
                    return jsonify({'error': f'PDF error: {str(e)}'}), 400
            else:
                return jsonify({'error': 'PDF support not installed'}), 400
        else:
            session_data['image_path'] = filepath
            with open(filepath, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_data,
            'filename': filename
        })"""

code = code.replace(old_upload, new_upload)

with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("PDF support added to backend!")
