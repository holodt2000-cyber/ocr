#!/usr/bin/env python3
"""OCR with text position detection and visualization."""

import sys
import os
import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Auto-detect Tesseract path on Windows
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

class OCRWithPositions:
    """OCR processor with text position detection."""
    
    def __init__(self, lang='eng+rus', confidence_threshold=60):
        self.lang = lang
        self.confidence_threshold = confidence_threshold
    
    def get_text_boxes(self, image_path):
        """Get text with bounding boxes and positions."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(img, lang=self.lang, output_type=pytesseract.Output.DICT)
        
        boxes = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            # Filter by confidence
            if int(data['conf'][i]) > self.confidence_threshold:
                text = data['text'][i].strip()
                if text:  # Skip empty strings
                    box = {
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i],
                        'block_num': data['block_num'][i],
                        'line_num': data['line_num'][i],
                        'word_num': data['word_num'][i]
                    }
                    boxes.append(box)
        
        return boxes, img
    
    def draw_boxes(self, image_path, output_path='output_with_boxes.png'):
        """Draw bounding boxes around detected text."""
        boxes, img = self.get_text_boxes(image_path)
        
        # Convert to PIL for better drawing
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Try to load a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        for box in boxes:
            x, y, w, h = box['x'], box['y'], box['width'], box['height']
            
            # Draw rectangle
            draw.rectangle([x, y, x + w, y + h], outline='red', width=2)
            
            # Draw confidence score
            conf_text = f"{box['confidence']}%"
            draw.text((x, y - 15), conf_text, fill='red', font=font)
        
        # Save result
        img_pil.save(output_path)
        logger.info(f"Saved image with boxes to: {output_path}")
        return output_path
    
    def get_structured_text(self, image_path):
        """Get text organized by lines and blocks."""
        boxes, _ = self.get_text_boxes(image_path)
        
        # Group by blocks and lines
        structured = {}
        for box in boxes:
            block_num = box['block_num']
            line_num = box['line_num']
            
            if block_num not in structured:
                structured[block_num] = {}
            
            if line_num not in structured[block_num]:
                structured[block_num][line_num] = []
            
            structured[block_num][line_num].append(box)
        
        return structured
    
    def export_to_html(self, image_path, output_path='output.html'):
        """Export OCR result to HTML with absolute positioning."""
        boxes, img = self.get_text_boxes(image_path)
        height, width = img.shape[:2]
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OCR Result</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        .container {{
            position: relative;
            width: {width}px;
            height: {height}px;
            border: 1px solid #ccc;
            background: #f9f9f9;
        }}
        .text-box {{
            position: absolute;
            border: 1px solid rgba(255, 0, 0, 0.3);
            background: rgba(255, 255, 255, 0.8);
            padding: 2px;
            font-size: 12px;
        }}
        .confidence {{
            font-size: 10px;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>OCR Result with Positions</h1>
    <div class="container">
'''
        
        for box in boxes:
            x, y, w, h = box['x'], box['y'], box['width'], box['height']
            text = box['text'].replace('<', '&lt;').replace('>', '&gt;')
            conf = box['confidence']
            
            html += f'''        <div class="text-box" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px;">
            <span>{text}</span>
            <span class="confidence">({conf}%)</span>
        </div>
'''
        
        html += '''    </div>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Saved HTML to: {output_path}")
        return output_path
    
    def print_text_with_positions(self, image_path):
        """Print text with their positions."""
        boxes, _ = self.get_text_boxes(image_path)
        
        print("\n=== Распознанный текст с позициями ===")
        print(f"Всего найдено слов: {len(boxes)}\n")
        
        for i, box in enumerate(boxes, 1):
            print(f"{i}. '{box['text']}'")
            print(f"   Позиция: x={box['x']}, y={box['y']}")
            print(f"   Размер: {box['width']}x{box['height']}")
            print(f"   Уверенность: {box['confidence']}%")
            print()

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python ocr_with_positions.py <image_path> [mode]")
        print("\nModes:")
        print("  boxes  - Draw boxes around text (default)")
        print("  html   - Export to HTML with positions")
        print("  print  - Print text with positions")
        print("  all    - Do all of the above")
        print("\nExample: python ocr_with_positions.py input.png boxes")
        sys.exit(1)
    
    image_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'boxes'
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    ocr = OCRWithPositions(lang='eng+rus', confidence_threshold=60)
    
    try:
        if mode in ['boxes', 'all']:
            output = ocr.draw_boxes(image_path)
            print(f"[OK] Создано изображение с рамками: {output}")
        
        if mode in ['html', 'all']:
            output = ocr.export_to_html(image_path)
            print(f"[OK] Создан HTML файл: {output}")
        
        if mode in ['print', 'all']:
            ocr.print_text_with_positions(image_path)
        
        print("\n[OK] Готово!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()