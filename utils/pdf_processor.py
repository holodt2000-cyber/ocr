#!/usr/bin/env python3
"""PDF processing utilities for OCR application."""

import os
import tempfile
from pathlib import Path
from typing import List, Optional
import logging

try:
    from pdf2image import convert_from_path
    from PIL import Image
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Process PDF files and convert to images for OCR."""
    
    def __init__(self, dpi: int = 300, poppler_path: Optional[str] = None):
        """
        Initialize PDF processor.
        
        Args:
            dpi: Resolution for PDF to image conversion (default: 300)
            poppler_path: Path to poppler binaries (Windows only)
        """
        if not PDF_SUPPORT:
            raise ImportError(
                "pdf2image is not installed. "
                "Install it with: pip install pdf2image"
            )
        
        self.dpi = dpi
        self.poppler_path = poppler_path
        
        # Auto-detect poppler on Windows
        if os.name == 'nt' and not poppler_path:
            self.poppler_path = self._find_poppler_windows()
    
    def _find_poppler_windows(self) -> Optional[str]:
        """Try to find poppler installation on Windows."""
        possible_paths = [
            r'C:\Program Files\poppler\Library\bin',
            r'C:\Program Files (x86)\poppler\Library\bin',
            os.path.expanduser(r'~\poppler\Library\bin'),
            r'C:\poppler\Library\bin',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found poppler at: {path}")
                return path
        
        logger.warning("Poppler not found. PDF conversion may fail.")
        logger.warning("See POPPLER_INSTALL.md for installation instructions.")
        return None
    
    def pdf_to_images(self, pdf_path: str, output_folder: Optional[str] = None) -> List[str]:
        """
        Convert PDF to images.
        
        Args:
            pdf_path: Path to PDF file
            output_folder: Folder to save images (optional, uses temp if not provided)
        
        Returns:
            List of paths to generated images
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Converting PDF to images: {pdf_path}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                poppler_path=self.poppler_path
            )
            
            # Determine output folder
            if output_folder:
                os.makedirs(output_folder, exist_ok=True)
            else:
                output_folder = tempfile.mkdtemp()
            
            # Save images
            image_paths = []
            pdf_name = Path(pdf_path).stem
            
            for i, image in enumerate(images, start=1):
                image_path = os.path.join(output_folder, f"{pdf_name}_page_{i}.png")
                image.save(image_path, 'PNG')
                image_paths.append(image_path)
                logger.info(f"Saved page {i} to: {image_path}")
            
            logger.info(f"Converted {len(images)} pages from PDF")
            return image_paths
        
        except Exception as e:
            logger.error(f"Failed to convert PDF: {e}")
            raise
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """
        Get number of pages in PDF.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Number of pages
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            images = convert_from_path(
                pdf_path,
                dpi=72,  # Low DPI just to count pages
                poppler_path=self.poppler_path
            )
            return len(images)
        except Exception as e:
            logger.error(f"Failed to get PDF page count: {e}")
            raise
    
    def pdf_page_to_image(self, pdf_path: str, page_number: int, 
                          output_path: Optional[str] = None) -> str:
        """
        Convert specific PDF page to image.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number (1-indexed)
            output_path: Output image path (optional)
        
        Returns:
            Path to generated image
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Converting PDF page {page_number}: {pdf_path}")
        
        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                first_page=page_number,
                last_page=page_number,
                poppler_path=self.poppler_path
            )
            
            if not images:
                raise ValueError(f"Page {page_number} not found in PDF")
            
            # Determine output path
            if not output_path:
                pdf_name = Path(pdf_path).stem
                temp_dir = tempfile.mkdtemp()
                output_path = os.path.join(temp_dir, f"{pdf_name}_page_{page_number}.png")
            
            # Save image
            images[0].save(output_path, 'PNG')
            logger.info(f"Saved page {page_number} to: {output_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to convert PDF page: {e}")
            raise