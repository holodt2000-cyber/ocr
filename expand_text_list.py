with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find and reduce edit panel height to give more space to list
html = html.replace(
    ".edit-panel {\n            padding: 20px;\n            background: #f8f9fa;\n            border-top: 2px solid #e0e0e0;\n        }",
    ".edit-panel {\n            padding: 15px;\n            background: #f8f9fa;\n            border-top: 2px solid #e0e0e0;\n            min-height: 120px;\n        }"
)

# Reduce sidebar header padding
html = html.replace(
    ".sidebar-header {\n            padding: 20px;\n            background: #f8f9fa;\n            border-bottom: 2px solid #e0e0e0;\n        }",
    ".sidebar-header {\n            padding: 15px;\n            background: #f8f9fa;\n            border-bottom: 2px solid #e0e0e0;\n        }"
)

# Make text-list take more space
html = html.replace(
    ".text-list {\n            flex: 1;\n            overflow-y: auto;\n            padding: 10px;\n        }",
    ".text-list {\n            flex: 1;\n            overflow-y: auto;\n            padding: 10px;\n            min-height: 400px;\n        }"
)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Text list area expanded!")
