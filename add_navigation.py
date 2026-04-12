import re

with open("web_app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add page navigation endpoints before the last line
insert_before = "if __name__ == '__main__':"

new_endpoints = """@app.route('/change_page', methods=['POST'])
def change_page():
    data = request.json
    page_num = data.get('page', 0)
    
    if 0 <= page_num < session_data['total_pages']:
        session_data['current_page'] = page_num
        current_page = session_data['pages'][page_num]
        
        with open(current_page['image_path'], 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_data,
            'boxes': current_page['text_boxes'],
            'show_background': current_page['show_background'],
            'current_page': page_num + 1,
            'total_pages': session_data['total_pages']
        })
    
    return jsonify({'error': 'Invalid page'}), 400

@app.route('/toggle_background', methods=['POST'])
def toggle_background():
    current_page = session_data['pages'][session_data['current_page']]
    current_page['show_background'] = not current_page.get('show_background', True)
    
    return jsonify({
        'success': True,
        'show_background': current_page['show_background']
    })

@app.route('/save_all_pages', methods=['GET'])
def save_all_pages():
    import zipfile
    from io import BytesIO
    
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, page_data in enumerate(session_data['pages']):
            img = Image.open(page_data['image_path'])
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
            
            for box in page_data['text_boxes']:
                x, y = box['x'], box['y']
                text = box['text']
                font_size = max(12, int(box['height'] * 0.8))
                
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                bbox = draw.textbbox((x, y), text, font=font)
                draw.rectangle(bbox, fill='white')
                draw.text((x, y), text, fill='black', font=font)
            
            page_buffer = BytesIO()
            img.save(page_buffer, format='PNG')
            page_buffer.seek(0)
            
            zip_file.writestr(f'page_{i+1}.png', page_buffer.getvalue())
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='ocr_pages.zip')

"""  

code = code.replace(insert_before, new_endpoints + "\n" + insert_before)

with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Page navigation endpoints added!")
