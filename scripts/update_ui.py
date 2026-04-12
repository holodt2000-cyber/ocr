with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Increase sidebar width for bigger list
html = html.replace(
    "width: 350px;",
    "width: 400px;"
)

# Update file input to accept PDF
html = html.replace(
    '''<input type="file" id="fileInput" accept="image/*">''',
    '''<input type="file" id="fileInput" accept="image/*,application/pdf">'''
)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated sidebar and PDF support!")
