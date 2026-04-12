with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Increase sidebar width
html = html.replace(
    ".sidebar {\n            width: 400px;",
    ".sidebar {\n            width: 450px;"
)

# Make text items more compact
html = html.replace(
    ".text-item {\n            padding: 15px;",
    ".text-item {\n            padding: 10px;"
)

# Reduce font size in list
html = html.replace(
    ".text-item-text {\n            font-weight: 600;\n            color: #333;\n            margin-bottom: 5px;\n        }",
    ".text-item-text {\n            font-weight: 600;\n            color: #333;\n            margin-bottom: 3px;\n            font-size: 14px;\n        }"
)

html = html.replace(
    ".text-item-info {\n            font-size: 12px;\n            color: #666;\n        }",
    ".text-item-info {\n            font-size: 11px;\n            color: #666;\n        }"
)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Sidebar expanded and list optimized!")
