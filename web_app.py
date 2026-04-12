#!/usr/bin/env python3
"""Web-based OCR editor using Flask."""

import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import json
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
    # Set poppler path for Windows
    import platform
    if platform.system() == 'Windows':
        poppler_path = r'C:\Program Files\poppler\Library\bin'
    else:
        poppler_path = None
except ImportError:
    PDF_SUPPORT = False
    poppler_path = None

# Auto-detect Tesseract
if os.name == 'nt':
    tesseract_paths = [
        os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'),
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tessdata_dir = os.path.join(os.path.dirname(path), 'tessdata')
            os.environ['TESSDATA_PREFIX'] = tessdata_dir
            break

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'ocr-editor-secret-key'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store current session data
session_data = {
    'pages': [],  # List of page objects
    'current_page': 0,
    'total_pages': 0
}

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload and process image."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        session_data['text_boxes'] = []
        
        # Handle PDF - convert all pages
        if filename.lower().endswith('.pdf'):
            if PDF_SUPPORT:
                try:
                    images = convert_from_path(filepath, poppler_path=poppler_path)
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
                img_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_data,
            'filename': filename
        })

@app.route('/ocr', methods=['POST'])
def run_ocr():
    """Run OCR on uploaded image."""
    if not session_data['pages']:
        return jsonify({'error': 'No image uploaded'}), 400
    
    try:
        current_page = session_data['pages'][session_data['current_page']]
        img = cv2.imread(current_page['image_path'])
        data = pytesseract.image_to_data(img, lang='eng+rus', output_type=pytesseract.Output.DICT)
        
        text_boxes = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60:
                text = data['text'][i].strip()
                if text:
                    box = {
                        'id': len(text_boxes),
                        'text': text,
                        'x': int(data['left'][i]),
                        'y': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i]),
                        'confidence': int(data['conf'][i])
                    }
                    text_boxes.append(box)
        
        session_data['pages'][session_data['current_page']]['text_boxes'] = text_boxes
        
        return jsonify({
            'success': True,
            'boxes': text_boxes,
            'count': len(text_boxes)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_box', methods=['POST'])
def update_box():
    """Update text box."""
    data = request.json
    box_id = data.get('id')
    new_text = data.get('text')
    
    if box_id is not None and new_text is not None:
        for box in session_data['pages'][session_data['current_page']]['text_boxes']:
            if box['id'] == box_id:
                box['text'] = new_text
                return jsonify({'success': True})
    
    return jsonify({'error': 'Box not found'}), 404

@app.route('/update_position', methods=['POST'])
def update_position():
    """Update text box position."""
    data = request.json
    box_id = data.get('id')
    new_x = data.get('x')
    new_y = data.get('y')
    
    if box_id is not None and new_x is not None and new_y is not None:
        for box in session_data['pages'][session_data['current_page']]['text_boxes']:
            if box['id'] == box_id:
                box['x'] = new_x
                box['y'] = new_y
                return jsonify({'success': True})
    
    return jsonify({'error': 'Box not found'}), 404

@app.route('/delete_box', methods=['POST'])
def delete_box():
    """Delete text box."""
    data = request.json
    box_id = data.get('id')
    
    if box_id is not None:
        session_data['pages'][session_data['current_page']]['text_boxes'] = [b for b in session_data['pages'][session_data['current_page']]['text_boxes'] if b['id'] != box_id]
        return jsonify({'success': True})
    
    return jsonify({'error': 'Box not found'}), 404

@app.route('/add_box', methods=['POST'])
def add_box():
    """Add new text box."""
    data = request.json
    
    new_box = {
        'id': len(session_data['pages'][session_data['current_page']]['text_boxes']),
        'text': data.get('text', 'New Label'),
        'x': int(data.get('x', 10)),
        'y': int(data.get('y', 10)),
        'width': int(data.get('width', 100)),
        'height': int(data.get('height', 30)),
        'confidence': 100
    }
    
    session_data['pages'][session_data['current_page']]['text_boxes'].append(new_box)
    
    return jsonify({
        'success': True,
        'box': new_box
    })

@app.route('/render_image', methods=['GET'])
def render_image():
    """Render image with text boxes."""
    if not session_data['pages']:
        return jsonify({'error': 'No image'}), 400
    
    try:
        # Load image
        img = Image.open(session_data['image_path'])
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        # Draw boxes
        for box in session_data['pages'][session_data['current_page']]['text_boxes']:
            x, y, w, h = box['x'], box['y'], box['width'], box['height']
            
            # Draw rectangle
            draw.rectangle([x, y, x + w, y + h], outline='red', width=2)
            
            # Draw text
            draw.text((x, y - 15), box['text'], fill='red', font=font)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_data = base64.b64encode(buffer.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_image', methods=['GET'])
def save_image():
    """Save rendered image with text overlay."""
    if not session_data['pages']:
        return jsonify({'error': 'No image'}), 400
    
    try:
        img = Image.open(session_data['image_path'])
        draw = ImageDraw.Draw(img)
        
        # Draw text directly on image
        for box in session_data['pages'][session_data['current_page']]['text_boxes']:
            x, y = box['x'], box['y']
            text = box['text']
            font_size = max(12, int(box['height'] * 0.8))
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Draw text with white background for visibility
            bbox = draw.textbbox((x, y), text, font=font)
            draw.rectangle(bbox, fill='white')
            draw.text((x, y), text, fill='black', font=font)
        
        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='edited_image.png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_boxes', methods=['GET'])
def get_boxes():
    """Get all text boxes."""
    return jsonify({
        'success': True,
        'boxes': session_data['pages'][session_data['current_page']]['text_boxes']
    })

@app.route('/change_page', methods=['POST'])
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


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  OCR Web Editor")
    print("="*60)
    print("\nServer starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)