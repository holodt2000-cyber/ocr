 #!/usr/bin/env python3
"""Edit text directly on image - replace recognized text with new text."""

import sys
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ocr_with_positions import OCRWithPositions

class ImageTextEditor:
    """Edit text on images."""
    
    def __init__(self, lang='eng+rus'):
        self.ocr = OCRWithPositions(lang=lang)
    
    def replace_text(self, image_path, old_text, new_text, output_path='edited_image.png'):
        """Replace specific text on image."""
        boxes, img = self.ocr.get_text_boxes(image_path)
        
        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Try to load font
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        replaced_count = 0
        for box in boxes:
            if old_text.lower() in box['text'].lower():
                x, y, w, h = box['x'], box['y'], box['width'], box['height']
                
                # Cover old text with white rectangle
                draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill='white')
                
                # Draw new text
                draw.text((x, y), new_text, fill='black', font=font)
                replaced_count += 1
                print(f"Заменено: '{box['text']}' → '{new_text}' на позиции ({x}, {y})")
        
        img_pil.save(output_path)
        print(f"\nВсего замен: {replaced_count}")
        print(f"Сохранено: {output_path}")
        return output_path
    
    def remove_text(self, image_path, text_to_remove, output_path='cleaned_image.png'):
        """Remove specific text from image."""
        boxes, img = self.ocr.get_text_boxes(image_path)
        
        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        removed_count = 0
        for box in boxes:
            if text_to_remove.lower() in box['text'].lower():
                x, y, w, h = box['x'], box['y'], box['width'], box['height']
                
                # Cover with white rectangle
                draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill='white')
                removed_count += 1
                print(f"Удалено: '{box['text']}' на позиции ({x}, {y})")
        
        img_pil.save(output_path)
        print(f"\nВсего удалений: {removed_count}")
        print(f"Сохранено: {output_path}")
        return output_path
    
    def highlight_text(self, image_path, text_to_highlight, output_path='highlighted_image.png', color='yellow'):
        """Highlight specific text on image."""
        boxes, img = self.ocr.get_text_boxes(image_path)
        
        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        highlighted_count = 0
        for box in boxes:
            if text_to_highlight.lower() in box['text'].lower():
                x, y, w, h = box['x'], box['y'], box['width'], box['height']
                
                # Draw semi-transparent highlight
                overlay = Image.new('RGBA', img_pil.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill=color + '80')  # 50% opacity
                
                img_pil = Image.alpha_composite(img_pil.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img_pil)
                
                highlighted_count += 1
                print(f"Выделено: '{box['text']}' на позиции ({x}, {y})")
        
        img_pil.save(output_path)
        print(f"\nВсего выделений: {highlighted_count}")
        print(f"Сохранено: {output_path}")
        return output_path

def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python edit_text_on_image.py <image_path> <command> [args]")
        print("\nCommands:")
        print("  replace <old_text> <new_text>  - Replace text")
        print("  remove <text>                   - Remove text")
        print("  highlight <text> [color]        - Highlight text")
        print("\nExamples:")
        print("  python edit_text_on_image.py input.png replace 'Атом' 'Молекула'")
        print("  python edit_text_on_image.py input.png remove 'ABYX'")
        print("  python edit_text_on_image.py input.png highlight 'фотон' yellow")
        sys.exit(1)
    
    image_path = sys.argv[1]
    command = sys.argv[2]
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    editor = ImageTextEditor(lang='eng+rus')
    
    try:
        if command == 'replace':
            if len(sys.argv) < 5:
                print("Error: replace requires <old_text> <new_text>")
                sys.exit(1)
            old_text = sys.argv[3]
            new_text = sys.argv[4]
            editor.replace_text(image_path, old_text, new_text)
        
        elif command == 'remove':
            if len(sys.argv) < 4:
                print("Error: remove requires <text>")
                sys.exit(1)
            text = sys.argv[3]
            editor.remove_text(image_path, text)
        
        elif command == 'highlight':
            if len(sys.argv) < 4:
                print("Error: highlight requires <text>")
                sys.exit(1)
            text = sys.argv[3]
            color = sys.argv[4] if len(sys.argv) > 4 else 'yellow'
            editor.highlight_text(image_path, text, color=color)
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
        
        print("\n[OK] Готово!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()