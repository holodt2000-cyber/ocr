import re

with open("web_app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Update OCR endpoint
code = code.replace(
    "if not session_data['image_path']:",
    "if not session_data['pages']:"
)

code = code.replace(
    "img = cv2.imread(session_data['image_path'])",
    "current_page = session_data['pages'][session_data['current_page']]\n        img = cv2.imread(current_page['image_path'])"
)

code = code.replace(
    "session_data['text_boxes'] = text_boxes",
    "session_data['pages'][session_data['current_page']]['text_boxes'] = text_boxes"
)

# Update get_boxes
code = code.replace(
    "return jsonify({\n        'success': True,\n        'boxes': session_data['text_boxes']\n    })",
    "return jsonify({\n        'success': True,\n        'boxes': session_data['pages'][session_data['current_page']]['text_boxes']\n    })"
)

# Update update_box
code = code.replace(
    "for box in session_data['text_boxes']:",
    "for box in session_data['pages'][session_data['current_page']]['text_boxes']:"
)

# Update delete_box
code = code.replace(
    "session_data['text_boxes'] = [b for b in session_data['text_boxes'] if b['id'] != box_id]",
    "session_data['pages'][session_data['current_page']]['text_boxes'] = [b for b in session_data['pages'][session_data['current_page']]['text_boxes'] if b['id'] != box_id]"
)

# Update add_box
code = code.replace(
    "new_box = {\n        'id': len(session_data['text_boxes']),",
    "new_box = {\n        'id': len(session_data['pages'][session_data['current_page']]['text_boxes']),"
)

code = code.replace(
    "session_data['text_boxes'].append(new_box)",
    "session_data['pages'][session_data['current_page']]['text_boxes'].append(new_box)"
)

with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Endpoints updated for multi-page!")
