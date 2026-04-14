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
import easyocr
import json
from utils.pdf_processor import PDFProcessor

# Initialize EasyOCR reader
print("Инициализация EasyOCR...")
try:
    reader = easyocr.Reader(['ru', 'en'], gpu=False)  # Используем CPU для совместимости с Render
    print("EasyOCR успешно инициализирован")
except Exception as e:
    print(f"Ошибка инициализации EasyOCR: {e}")
    reader = None

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
        return jsonify({'error': 'Файл не загружен'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Неверный тип файла. Разрешены: PNG, JPG, JPEG, BMP, TIFF, PDF'}), 400
    
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
                pdf_name = os.path.splitext(filename)[0]
                first_page_output = os.path.join(app.config['UPLOAD_FOLDER'], f"{pdf_name}_page_1.png")
                first_page_path = pdf_processor.pdf_page_to_image(
                    filepath, 1, first_page_output
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
                return jsonify({'error': f'Ошибка обработки PDF: {str(e)}'}), 500
        elif is_pdf and not PDF_AVAILABLE:
            return jsonify({'error': 'Поддержка PDF недоступна. См. POPPLER_INSTALL.md'}), 400
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
        return jsonify({'error': 'Изображение не загружено'}), 400
    
    if reader is None:
        return jsonify({'error': 'EasyOCR не инициализирован'}), 500
    
    try:
        img = cv2.imread(session_data['image_path'])
        if img is None:
            return jsonify({'error': 'Не удалось загрузить изображение'}), 400
        
        # EasyOCR возвращает список [bbox, text, confidence]
        results = reader.readtext(session_data['image_path'])
        
        text_boxes = []
        for i, (bbox, text, conf) in enumerate(results):
            # bbox это [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            x = int(min(x_coords))
            y = int(min(y_coords))
            width = int(max(x_coords) - min(x_coords))
            height = int(max(y_coords) - min(y_coords))
            
            box = {
                'id': i,
                'text': text,
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'confidence': int(conf * 100)
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
    
    return jsonify({'error': 'Элемент не найден'}), 404

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
    
    return jsonify({'error': 'Элемент не найден'}), 404

@app.route('/delete_box', methods=['POST'])
def delete_box():
    """Delete text box."""
    data = request.json
    box_id = data.get('id')
    
    if box_id is not None:
        session_data['text_boxes'] = [b for b in session_data['text_boxes'] if b['id'] != box_id]
        return jsonify({'success': True})
    
    return jsonify({'error': 'Элемент не найден'}), 404

@app.route('/add_box', methods=['POST'])
def add_box():
    """Add new text box."""
    data = request.json
    
    new_box = {
        'id': len(session_data['text_boxes']),
        'text': data.get('text', 'Новая метка'),
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
        return jsonify({'error': 'Нет изображения'}), 400
    
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
        return jsonify({'error': 'Нет изображения'}), 400
    
    if not os.path.exists(session_data['image_path']):
        return jsonify({'error': 'Файл изображения не найден'}), 404
    
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
        return jsonify({'error': 'Это не PDF документ'}), 400
    
    data = request.json
    page_number = data.get('page', 1) - 1  # Convert to 0-indexed
    
    if page_number < 0 or page_number >= session_data['pdf_page_count']:
        return jsonify({'error': 'Неверный номер страницы'}), 400
    
    try:
                # Check if page is already cached
        if page_number in session_data['page_cache']:
            image_path = session_data['page_cache'][page_number]
        else:
            # Convert page on demand
            pdf_name = os.path.splitext(os.path.basename(session_data['pdf_path']))[0]
            page_output = os.path.join(app.config['UPLOAD_FOLDER'], f"{pdf_name}_page_{page_number + 1}.png")
            image_path = pdf_processor.pdf_page_to_image(
                session_data['pdf_path'],
                page_number + 1,  # 1-indexed for pdf_processor
                page_output
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
    print("  Архивариус OCR - Веб-редактор")
    print("="*60)
    print("\nСервер запускается...")
    print("Откройте браузер: http://localhost:5000")
    print("\nДля остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)