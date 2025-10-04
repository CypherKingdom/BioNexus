import pytesseract
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import os
import logging
from typing import List, Tuple, Optional
import re

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        # Configure Tesseract path if needed
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[Image.Image]:
        """Convert PDF to list of PIL Images."""
        try:
            images = convert_from_path(pdf_path, dpi=dpi, thread_count=4)
            logger.info(f"Converted PDF to {len(images)} images: {pdf_path}")
            return images
        except Exception as e:
            logger.error(f"Failed to convert PDF {pdf_path}: {e}")
            raise
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        # Convert PIL to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply thresholding to get better contrast
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        return Image.fromarray(thresh)
    
    def extract_text_from_image(self, image: Image.Image, preprocess: bool = True) -> Tuple[str, float]:
        """Extract text from image using Tesseract OCR."""
        try:
            if preprocess:
                image = self.preprocess_image(image)
            
            # OCR configuration for scientific documents
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,;:!?()[]{}\"\'%-+=/\\@#$%^&*_|~`<> \t\n'
            
            # Extract text with confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
            text = pytesseract.image_to_string(image, config=config)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return self.clean_text(text), avg_confidence / 100.0
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "", 0.0
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # In certain contexts
        
        # Remove artifacts
        text = re.sub(r'[^\w\s.,;:!?()\[\]{}"\'%-+=/@#$%^&*_|~`<>]', '', text)
        
        return text.strip()
    
    def segment_sections(self, text: str) -> dict:
        """Segment document text into sections using heuristics."""
        sections = {
            'title': '',
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'references': '',
            'figures': [],
            'tables': []
        }
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_section = 'title'
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Section detection patterns
            if any(keyword in para_lower for keyword in ['abstract']):
                current_section = 'abstract'
                continue
            elif any(keyword in para_lower for keyword in ['introduction', 'background']):
                current_section = 'introduction'
                continue
            elif any(keyword in para_lower for keyword in ['method', 'material', 'procedure']):
                current_section = 'methods'
                continue
            elif any(keyword in para_lower for keyword in ['result', 'finding']):
                current_section = 'results'
                continue
            elif any(keyword in para_lower for keyword in ['discussion', 'analysis']):
                current_section = 'discussion'
                continue
            elif any(keyword in para_lower for keyword in ['conclusion', 'summary']):
                current_section = 'conclusion'
                continue
            elif any(keyword in para_lower for keyword in ['reference', 'bibliography']):
                current_section = 'references'
                continue
            elif 'figure' in para_lower or 'fig.' in para_lower:
                sections['figures'].append(para)
                continue
            elif 'table' in para_lower:
                sections['tables'].append(para)
                continue
            
            # Add to current section
            if current_section in sections and isinstance(sections[current_section], str):
                sections[current_section] += ' ' + para
        
        # Clean up sections
        for key in sections:
            if isinstance(sections[key], str):
                sections[key] = sections[key].strip()
        
        return sections
    
    def extract_figures_tables(self, image: Image.Image) -> Tuple[List[dict], List[dict]]:
        """Extract figures and tables from image using basic detection."""
        figures = []
        tables = []
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect horizontal and vertical lines (tables)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        
        # Find contours for potential tables
        contours, _ = cv2.findContours(
            horizontal_lines + vertical_lines, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                tables.append({
                    'type': 'table',
                    'bbox': [x, y, x+w, y+h],
                    'confidence': 0.7
                })
        
        # Simple figure detection (remaining large areas)
        # This is a basic implementation - in production use more sophisticated methods
        
        return figures, tables
    
    def process_pdf(self, pdf_path: str, output_dir: str) -> List[dict]:
        """Complete PDF processing pipeline."""
        results = []
        
        try:
            # Convert PDF to images
            images = self.pdf_to_images(pdf_path)
            
            for i, image in enumerate(images):
                page_num = i + 1
                
                # Extract text
                text, confidence = self.extract_text_from_image(image)
                
                # Segment sections
                sections = self.segment_sections(text)
                
                # Extract figures and tables
                figures, tables = self.extract_figures_tables(image)
                
                # Save page image
                image_path = os.path.join(output_dir, f"page_{page_num:03d}.png")
                image.save(image_path)
                
                page_result = {
                    'page_number': page_num,
                    'text': text,
                    'confidence': confidence,
                    'sections': sections,
                    'figures': figures,
                    'tables': tables,
                    'image_path': image_path
                }
                
                results.append(page_result)
                logger.info(f"Processed page {page_num}/{len(images)} with {len(text)} characters")
            
            return results
            
        except Exception as e:
            logger.error(f"PDF processing failed for {pdf_path}: {e}")
            raise


# Global OCR service instance
ocr_service = OCRService()