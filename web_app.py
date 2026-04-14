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
from utils.pdf_processor import PDFProcessor

# Auto-detect Tesseract
tesseract_found = False
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
            tesseract_found = True
            print(f"Tesseract найден: {path}")
            break

if not tesseract_found and os.name == 'nt':
    print("\n" + "="*60)
    print("ВНИМАНИЕ: Tesseract OCR не найден!")
    print("="*60)
    print("Установите Tesseract OCR для работы приложения.")
    print("См. POPPLER_INSTALL.md для инструкций.")
    print("="*60 + "\n")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'ocr-editor-secret-key'

# Store current session data
session_data = {
    'image_path': None,
    'text_boxes': [],
    'pdf_path': None,
    'pdf_page_count': 0,
    'current_page': 0,
    'is_pdf': False,
    'page_cache': {}  # Cache for converted pages
}

# Initialize PDF processor
try:
    pdf_processor = PDFProcessor()
    PDF_AVAILABLE = True
except Exception as e:
    print(f"PDF support not available: {e}")
    PDF_AVAILABLE = False

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload and process image."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, BMP, TIFF, PDF'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
                # Check if PDF
        is_pdf = filename.lower().endswith('.pdf')
        
        if is_pdf and PDF_AVAILABLE:
            try:
                # Get page count without converting all pages
                page_count = pdf_processor.get_pdf_page_count(filepath)
                
                # Convert only first page
                first_page_path = pdf_processor.pdf_page_to_image(
                    filepath, 1, app.config['UPLOAD_FOLDER']
                )
                
                session_data['pdf_path'] = filepath
                session_data['pdf_page_count'] = page_count
                session_data['current_page'] = 0
                session_data['is_pdf'] = True
                session_data['image_path'] = first_page_path
                session_data['text_boxes'] = []
                session_data['page_cache'] = {0: first_page_path}
                
                                # Convert first page to base64
                with open(first_page_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'image': img_data,
                    'filename': filename,
                    'is_pdf': True,
                    'total_pages': page_count,
                    'current_page': 1
                                })
            except Exception as e:
                return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
        elif is_pdf and not PDF_AVAILABLE:
            return jsonify({'error': 'PDF support not available. See POPPLER_INSTALL.md'}), 400
        else:
            session_data['image_path'] = filepath
            session_data['text_boxes'] = []
            session_data['is_pdf'] = False
            session_data['pdf_path'] = None
            session_data['pdf_page_count'] = 0
            session_data['page_cache'] = {}
            
            # Convert image to base64 for display
            with open(filepath, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'image': img_data,
                'filename': filename,
                'is_pdf': False
            })

@app.route('/ocr', methods=['POST'])
def run_ocr():
    """Run OCR on uploaded image."""
    if not session_data['image_path']:
        return jsonify({'error': 'No image uploaded'}), 400
    
    try:
        img = cv2.imread(session_data['image_path'])
        if img is None:
            return jsonify({'error': 'Failed to load image'}), 400
        
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
        
        session_data['text_boxes'] = text_boxes
        
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
        for box in session_data['text_boxes']:
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
        for box in session_data['text_boxes']:
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
        session_data['text_boxes'] = [b for b in session_data['text_boxes'] if b['id'] != box_id]
        return jsonify({'success': True})
    
    return jsonify({'error': 'Box not found'}), 404

@app.route('/add_box', methods=['POST'])
def add_box():
    """Add new text box."""
    data = request.json
    
    new_box = {
        'id': len(session_data['text_boxes']),
        'text': data.get('text', 'New Label'),
        'x': int(data.get('x', 10)),
        'y': int(data.get('y', 10)),
        'width': int(data.get('width', 100)),
        'height': int(data.get('height', 30)),
        'confidence': 100
    }
    
    session_data['text_boxes'].append(new_box)
    
    return jsonify({
        'success': True,
        'box': new_box
    })

@app.route('/render_image', methods=['GET'])
def render_image():
    """Render image with text boxes."""
    if not session_data['image_path']:
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
        for box in session_data['text_boxes']:
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
    if not session_data['image_path']:
        return jsonify({'error': 'No image'}), 400
    
    if not os.path.exists(session_data['image_path']):
        return jsonify({'error': 'Image file not found'}), 404
    
    try:
        img = Image.open(session_data['image_path'])
        draw = ImageDraw.Draw(img)
        
        # Draw text directly on image
        for box in session_data['text_boxes']:
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
        'boxes': session_data['text_boxes']
    })

@app.route('/pdf_page', methods=['POST'])
def change_pdf_page():
    """Change current PDF page (lazy loading)."""
    if not session_data['is_pdf']:
        return jsonify({'error': 'Not a PDF document'}), 400
    
    data = request.json
    page_number = data.get('page', 1) - 1  # Convert to 0-indexed
    
    if page_number < 0 or page_number >= session_data['pdf_page_count']:
        return jsonify({'error': 'Invalid page number'}), 400
    
    try:
        # Check if page is already cached
        if page_number in session_data['page_cache']:
            image_path = session_data['page_cache'][page_number]
        else:
            # Convert page on demand
            image_path = pdf_processor.pdf_page_to_image(
                session_data['pdf_path'],
                page_number + 1,  # 1-indexed for pdf_processor
                app.config['UPLOAD_FOLDER']
            )
            # Cache the converted page
            session_data['page_cache'][page_number] = image_path
        
        session_data['current_page'] = page_number
        session_data['image_path'] = image_path
        session_data['text_boxes'] = []  # Clear text boxes for new page
        
        # Convert page to base64
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_data,
            'current_page': page_number + 1,
            'total_pages': session_data['pdf_page_count']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pdf_info', methods=['GET'])
def get_pdf_info():
    """Get PDF information."""
    return jsonify({
        'is_pdf': session_data['is_pdf'],
        'total_pages': session_data['pdf_page_count'] if session_data['is_pdf'] else 0,
        'current_page': session_data['current_page'] + 1 if session_data['is_pdf'] else 0
    })

if __name__ == '__main__':
    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("\n" + "="*60)
    print("  OCR Web Editor")
    print("="*60)
    print("\nСервер запускается...")
    print("Откройте браузер: http://localhost:5000")
    print("\nДля остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)