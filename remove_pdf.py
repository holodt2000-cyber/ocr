with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove PDF from accept
html = html.replace(
    '''<input type="file" id="fileInput" accept="image/*,application/pdf">''',
    '''<input type="file" id="fileInput" accept="image/*">'''
)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("PDF removed from UI")
