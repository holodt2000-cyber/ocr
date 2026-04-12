with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Increase sidebar even more
html = html.replace(
    ".sidebar {\n            width: 450px;",
    ".sidebar {\n            width: 500px;"
)

# Add PDF back
html = html.replace(
    '''<input type="file" id="fileInput" accept="image/*">''',
    '''<input type="file" id="fileInput" accept="image/*,application/pdf">'''
)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Sidebar expanded to 500px and PDF support restored!")
