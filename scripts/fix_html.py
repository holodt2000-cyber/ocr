import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update text-overlay CSS
old = r'.text-overlay {\s+position: absolute;\s+cursor: move;\s+user-select: text;\s+padding: 2px 4px;\s+font-family: Arial, sans-serif;\s+white-space: nowrap;\s+transition: background 0.2s;\s+}'

new = '''.text-overlay {
            position: absolute;
            cursor: move;
            user-select: text;
            padding: 3px 6px;
            font-family: Arial, sans-serif;
            white-space: nowrap;
            transition: all 0.2s;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(0, 0, 0, 0.15);
            border-radius: 3px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }'''

html = re.sub(old, new, html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated!')
