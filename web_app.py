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
    'image_path': None,
    'text_boxes': []
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
        
        session_data['image_path'] = filepath
        session_data['text_boxes'] = []
        
        # Convert image to base64 for display
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
    if not session_data['image_path']:
        return jsonify({'error': 'No image uploaded'}), 400
    
    try:
        img = cv2.imread(session_data['image_path'])
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
    """Save rendered image."""
    if not session_data['image_path']:
        return jsonify({'error': 'No image'}), 400
    
    try:
        img = Image.open(session_data['image_path'])
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        for box in session_data['text_boxes']:
            x, y, w, h = box['x'], box['y'], box['width'], box['height']
            draw.rectangle([x, y, x + w, y + h], outline='red', width=2)
            draw.text((x, y - 15), box['text'], fill='red', font=font)
        
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  OCR Web Editor")
    print("="*60)
    print("\nServer starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)