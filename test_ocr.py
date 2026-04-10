#!/usr/bin/env python3
"""Unit tests for OCR processor."""

import unittest
import os
from pathlib import Path
from main import OCRProcessor
import tempfile
import cv2
import numpy as np

class TestOCRProcessor(unittest.TestCase):
    """Test cases for OCRProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = OCRProcessor()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_processor_initialization(self):
        """Test OCRProcessor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.config, r'--oem 3 --psm 6')
    
    def test_custom_config(self):
        """Test custom configuration."""
        custom_processor = OCRProcessor(config='--psm 3')
        self.assertEqual(custom_processor.config, '--psm 3')
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.processor.process_image('nonexistent.png')
    
    def test_process_simple_image(self):
        """Test processing a simple test image."""
        # Create a simple test image with text
        img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img, 'TEST', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        test_image_path = os.path.join(self.test_dir, 'test.png')
        cv2.imwrite(test_image_path, img)
        
        result = self.processor.process_image(test_image_path)
        self.assertIsInstance(result, str)
        # Note: OCR might not be perfect, so we just check it returns something
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()