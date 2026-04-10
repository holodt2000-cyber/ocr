#!/usr/bin/env python3
"""Interactive OCR text editor with GUI."""

import sys
import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pytesseract
from pathlib import Path

# Auto-detect Tesseract
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

class TextBox:
    """Represents a text box on the image."""
    def __init__(self, text, x, y, width, height, confidence=100):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.confidence = confidence
        self.selected = False

class InteractiveOCREditor:
    """Interactive OCR editor with GUI."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive OCR Editor")
        self.root.geometry("1200x800")
        
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.photo = None
        self.text_boxes = []
        self.selected_box = None
        self.scale = 1.0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface."""
        # Top toolbar
        toolbar = tk.Frame(self.root, bg='#f0f0f0', height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(toolbar, text="📁 Open Image", command=self.load_image, 
                 bg='#4CAF50', fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="🔍 Run OCR", command=self.run_ocr,
                 bg='#2196F3', fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="💾 Save Image", command=self.save_image,
                 bg='#FF9800', fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="➕ Add Label", command=self.add_label,
                 bg='#9C27B0', fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="🗑️ Delete Selected", command=self.delete_selected,
                 bg='#F44336', fg='white', padx=10, pady=5).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Image canvas
        left_panel = tk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        canvas_frame = tk.Frame(left_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#e0e0e0')
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Right panel - Text boxes list
        right_panel = tk.Frame(main_container, width=300, bg='white')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="Detected Text", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(right_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, font=('Arial', 10))
        self.text_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.text_listbox.yview)
        
        self.text_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # Edit panel
        edit_frame = tk.LabelFrame(right_panel, text="Edit Selected", bg='white', padx=10, pady=10)
        edit_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(edit_frame, text="Text:", bg='white').pack(anchor=tk.W)
        self.edit_text = tk.Entry(edit_frame, font=('Arial', 12))
        self.edit_text.pack(fill=tk.X, pady=5)
        
        tk.Button(edit_frame, text="Update", command=self.update_text,
                 bg='#4CAF50', fg='white').pack(fill=tk.X, pady=5)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_image(self):
        """Load image from file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.display_image = self.original_image.copy()
            self.text_boxes = []
            self.update_canvas()
            self.status_bar.config(text=f"Loaded: {Path(file_path).name}")
    
    def run_ocr(self):
        """Run OCR on the image."""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please load an image first!")
            return
        
        self.status_bar.config(text="Running OCR...")
        self.root.update()
        
        try:
            # Convert PIL to OpenCV
            img_cv = cv2.cvtColor(np.array(self.original_image), cv2.COLOR_RGB2BGR)
            
            # Get OCR data
            data = pytesseract.image_to_data(img_cv, lang='eng+rus', output_type=pytesseract.Output.DICT)
            
            self.text_boxes = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                if int(data['conf'][i]) > 60:
                    text = data['text'][i].strip()
                    if text:
                        box = TextBox(
                            text=text,
                            x=data['left'][i],
                            y=data['top'][i],
                            width=data['width'][i],
                            height=data['height'][i],
                            confidence=data['conf'][i]
                        )
                        self.text_boxes.append(box)
            
            self.update_canvas()
            self.update_listbox()
            self.status_bar.config(text=f"OCR complete: {len(self.text_boxes)} text boxes found")
            
        except Exception as e:
            messagebox.showerror("OCR Error", str(e))
            self.status_bar.config(text="OCR failed")
    
    def update_canvas(self):
        """Update canvas with image and text boxes."""
        if not self.original_image:
            return
        
        # Create display image with boxes
        self.display_image = self.original_image.copy()
        draw = ImageDraw.Draw(self.display_image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        for box in self.text_boxes:
            color = 'red' if box.selected else 'blue'
            width = 3 if box.selected else 2
            
            # Draw rectangle
            draw.rectangle(
                [box.x, box.y, box.x + box.width, box.y + box.height],
                outline=color, width=width
            )
            
            # Draw text
            draw.text((box.x, box.y - 15), box.text, fill=color, font=font)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def update_listbox(self):
        """Update listbox with text boxes."""
        self.text_listbox.delete(0, tk.END)
        for i, box in enumerate(self.text_boxes):
            self.text_listbox.insert(tk.END, f"{i+1}. {box.text} ({box.confidence}%)")
    
    def on_canvas_click(self, event):
        """Handle canvas click."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Find clicked box
        for box in self.text_boxes:
            if (box.x <= x <= box.x + box.width and 
                box.y <= y <= box.y + box.height):
                self.select_box(box)
                return
        
        # Deselect all
        self.select_box(None)
    
    def on_canvas_drag(self, event):
        """Handle canvas drag."""
        pass
    
    def on_canvas_release(self, event):
        """Handle canvas release."""
        pass
    
    def on_listbox_select(self, event):
        """Handle listbox selection."""
        selection = self.text_listbox.curselection()
        if selection:
            idx = selection[0]
            self.select_box(self.text_boxes[idx])
    
    def select_box(self, box):
        """Select a text box."""
        # Deselect all
        for b in self.text_boxes:
            b.selected = False
        
        # Select new box
        if box:
            box.selected = True
            self.selected_box = box
            self.edit_text.delete(0, tk.END)
            self.edit_text.insert(0, box.text)
        else:
            self.selected_box = None
            self.edit_text.delete(0, tk.END)
        
        self.update_canvas()
    
    def update_text(self):
        """Update selected text box."""
        if self.selected_box:
            new_text = self.edit_text.get()
            self.selected_box.text = new_text
            self.update_canvas()
            self.update_listbox()
            self.status_bar.config(text="Text updated")
    
    def add_label(self):
        """Add new text label."""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please load an image first!")
            return
        
        # Simple dialog for new label
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Label")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Text:").pack(pady=5)
        text_entry = tk.Entry(dialog)
        text_entry.pack(pady=5)
        
        tk.Label(dialog, text="X:").pack(pady=5)
        x_entry = tk.Entry(dialog)
        x_entry.insert(0, "10")
        x_entry.pack(pady=5)
        
        tk.Label(dialog, text="Y:").pack(pady=5)
        y_entry = tk.Entry(dialog)
        y_entry.insert(0, "10")
        y_entry.pack(pady=5)
        
        def add():
            text = text_entry.get()
            x = int(x_entry.get())
            y = int(y_entry.get())
            
            box = TextBox(text, x, y, len(text) * 10, 20, 100)
            self.text_boxes.append(box)
            self.update_canvas()
            self.update_listbox()
            dialog.destroy()
            self.status_bar.config(text="Label added")
        
        tk.Button(dialog, text="Add", command=add).pack(pady=10)
    
    def delete_selected(self):
        """Delete selected text box."""
        if self.selected_box:
            self.text_boxes.remove(self.selected_box)
            self.selected_box = None
            self.update_canvas()
            self.update_listbox()
            self.status_bar.config(text="Text box deleted")
    
    def save_image(self):
        """Save edited image."""
        if not self.display_image:
            messagebox.showwarning("No Image", "No image to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            self.display_image.save(file_path)
            self.status_bar.config(text=f"Saved: {Path(file_path).name}")
            messagebox.showinfo("Success", "Image saved successfully!")

def main():
    """Main entry point."""
    root = tk.Tk()
    app = InteractiveOCREditor(root)
    root.mainloop()

if __name__ == "__main__":
    import numpy as np
    main()