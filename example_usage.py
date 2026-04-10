#!/usr/bin/env python3
"""Примеры использования OCR процессора."""

from main import OCRProcessor
import cv2
import numpy as np
import os

def create_sample_image():
    """Создать пример изображения с текстом."""
    # Создаем белое изображение
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    
    # Добавляем текст
    text = "Hello OCR World!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 100), font, 1.5, (0, 0, 0), 3)
    
    # Сохраняем как input.png
    cv2.imwrite('input.png', img)
    print("[OK] Создан файл input.png с примером текста")

def example_basic_usage():
    """Базовое использование."""
    print("\n=== Пример 1: Базовое использование (английский) ===")
    processor = OCRProcessor(lang='eng')
    
    if os.path.exists('input.png'):
        result = processor.process_default_input()
        print(f"Распознанный текст: {result}")
    else:
        print("Файл input.png не найден. Создайте его с помощью create_sample_image()")

def example_multilang_usage():
    """Использование с несколькими языками."""
    print("\n=== Пример 2: Английский + Русский ===")
    processor = OCRProcessor(lang='eng+rus')
    
    if os.path.exists('input.png'):
        result = processor.process_default_input()
        print(f"Распознанный текст: {result}")
    else:
        print("Файл input.png не найден.")

def example_custom_config():
    """Использование с кастомной конфигурацией."""
    print("\n=== Пример 3: Кастомная конфигурация ===")
    # PSM 3 = Fully automatic page segmentation
    processor = OCRProcessor(config='--oem 3 --psm 3', lang='eng')
    
    if os.path.exists('input.png'):
        result = processor.process_image('input.png')
        print(f"Распознанный текст: {result}")

def example_batch_processing():
    """Пакетная обработка нескольких изображений."""
    print("\n=== Пример 4: Пакетная обработка ===")
    processor = OCRProcessor(lang='eng+rus')
    
    # Список файлов для обработки
    image_files = ['input.png']  # Добавьте больше файлов при необходимости
    
    for img_file in image_files:
        if os.path.exists(img_file):
            try:
                result = processor.process_image(img_file)
                print(f"\n{img_file}:")
                print(f"  {result}")
            except Exception as e:
                print(f"Ошибка при обработке {img_file}: {e}")

if __name__ == "__main__":
    print("=== Примеры использования OCR ===")
    
    # Создаем пример изображения
    create_sample_image()
    
    # Запускаем примеры
    example_basic_usage()
    example_multilang_usage()
    example_custom_config()
    example_batch_processing()
    
    print("\n=== Все примеры выполнены ===")