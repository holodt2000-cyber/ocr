with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add background toggle button in toolbar
html = html.replace(
    '''<button class="btn btn-danger" onclick="deleteSelected()">
                🗑️ Удалить
            </button>''',
    '''<button class="btn btn-danger" onclick="deleteSelected()">
                🗑️ Удалить
            </button>
            
            <button class="btn btn-info" onclick="toggleBackground()" id="bgToggleBtn" style="background: #607D8B;">
                🖼️ Белый фон
            </button>'''
)

# Add background toggle function in JavaScript
html = html.replace(
    '''function showLoading(show) {
            document.getElementById('loading').classList.toggle('active', show);
        }''',
    '''function showLoading(show) {
            document.getElementById('loading').classList.toggle('active', show);
        }
        
        function toggleBackground() {
            const canvas = document.getElementById('imageCanvas');
            const btn = document.getElementById('bgToggleBtn');
            const container = document.getElementById('imageContainer');
            
            if (canvas.style.display === 'none') {
                canvas.style.display = 'block';
                container.style.background = 'white';
                btn.textContent = '🖼️ Белый фон';
            } else {
                canvas.style.display = 'none';
                container.style.background = 'white';
                btn.textContent = '🖼️ Показать изображение';
            }
        }'''
)

# Replace addLabel function with click-to-add
html = html.replace(
    '''async function addLabel() {
            const text = prompt('Введите текст метки:');
            if (!text) return;
            
            const x = prompt('X координата:', '10');
            const y = prompt('Y координата:', '10');''',
    '''let addMode = false;
        
        function toggleAddMode() {
            addMode = !addMode;
            const btn = document.getElementById('addModeBtn');
            const container = document.getElementById('imageContainer');
            
            if (addMode) {
                btn.style.background = '#4CAF50';
                btn.textContent = '✓ Кликните на изображение';
                container.style.cursor = 'crosshair';
                setStatus('Режим добавления: кликните и введите текст');
            } else {
                btn.style.background = '#9C27B0';
                btn.textContent = '➕ Добавить метку';
                container.style.cursor = 'default';
                setStatus('Готов');
            }
        }
        
        async function addLabel() {
            const text = prompt('Введите текст метки:');
            if (!text) return;
            
            const x = 10;
            const y = 10;'''
)

# Update button onclick
html = html.replace(
    '''<button class="btn btn-purple" onclick="addLabel()">
                ➕ Добавить метку
            </button>''',
    '''<button class="btn btn-purple" onclick="toggleAddMode()" id="addModeBtn">
                ➕ Добавить метку
            </button>'''
)

# Add click handler for image container
html = html.replace(
    '''document.getElementById('fileInput').addEventListener('change', uploadImage);''',
    '''document.getElementById('fileInput').addEventListener('change', uploadImage);
        
        document.getElementById('imageContainer').addEventListener('click', function(e) {
            if (addMode && (e.target.id === 'imageCanvas' || e.target.id === 'textOverlay')) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const text = prompt('Введите текст:');
                if (text) {
                    saveNewLabel(text, x, y);
                    toggleAddMode();
                }
            }
        });
        
        async function saveNewLabel(text, x, y) {
            try {
                const response = await fetch('/add_box', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text, x, y, width: text.length * 10, height: 20})
                });
                const data = await response.json();
                if (data.success) {
                    boxes.push(data.box);
                    updateTextList();
                    renderTextOverlay();
                    setStatus('Метка добавлена');
                }
            } catch (error) {
                alert('Ошибка: ' + error);
            }
        }'''
)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML updated with background toggle and click-to-add!")
