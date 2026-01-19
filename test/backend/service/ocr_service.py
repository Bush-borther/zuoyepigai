from paddleocr import PaddleOCR
from pathlib import Path
import logging
import os

# M1/Mac optimization to prevent OpenMP crash
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Configure logging
logging.getLogger("ppocr").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, use_gpu: bool = False):
        # Initialize PaddleOCR
        # use_angle_cls=True enables orientation classification
        # lang="ch" for Chinese support
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")

    def extract_text(self, image_path: str | Path) -> list[dict]:
        """
        Extract text from image using PaddleOCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing text, confidence, and bounding box.
            Format: [{'text': str, 'confidence': float, 'box': [[x,y], ...]}, ...]
        """
        image_path_str = str(image_path)
        result = self.ocr.ocr(image_path_str)
        
        extracted_data = []
        
        # PaddleOCR result structure can vary
        # Result can be None if no text found
        logger.info(f"OCR result type: {type(result)}")
        logger.info(f"OCR result length: {len(result) if result else 0}")
        
        if not result:
            return []
        
        # result is usually a list with one element (the page)
        # Check if result[0] exists and is iterable
        if len(result) == 0:
            return []
            
        page_result = result[0]
        logger.info(f"Page result type: {type(page_result)}")
        
        # Handle OCRResult object (new PaddleOCR version)
        if hasattr(page_result, 'json'):
            # Convert OCRResult to dict
            page_data = page_result.json
            logger.info(f"OCRResult.json type: {type(page_data)}")
            
            # The actual data is in page_data['res']
            if isinstance(page_data, dict) and 'res' in page_data:
                actual_data = page_data['res']
                logger.info(f"Found 'res' key, type: {type(actual_data)}")
                
                if isinstance(actual_data, dict):
                    logger.info(f"actual_data keys: {list(actual_data.keys())}")
                    
                    # Extract text regions - use correct key names
                    boxes = actual_data.get('dt_polys', [])
                    texts = actual_data.get('rec_texts', [])  # Note: plural!
                    scores = actual_data.get('rec_scores', [1.0] * len(texts))  # Note: plural!
                    
                    logger.info(f"Found {len(boxes)} boxes, {len(texts)} texts")
                    
                    for i, (box, text, score) in enumerate(zip(boxes, texts, scores)):
                        if i == 0:
                            logger.info(f"First item: text='{text}', box={box}, score={score}")
                        
                        extracted_data.append({
                            "text": text,
                            "confidence": score,
                            "box": box
                        })
                else:
                    logger.warning(f"actual_data is not a dict: {type(actual_data)}")
            else:
                logger.warning(f"No 'res' key in page_data. Keys: {list(page_data.keys()) if isinstance(page_data, dict) else 'not a dict'}")
        elif isinstance(page_result, list):
            # Old format: list of [box, (text, score)]
            # Debug: log the first line to see structure
            if len(page_result) > 0:
                logger.info(f"First OCR line: {page_result[0]}")
                logger.info(f"First OCR line type: {type(page_result[0])}")
                if len(page_result[0]) > 0:
                    logger.info(f"First OCR line[0]: {page_result[0][0]}, type: {type(page_result[0][0])}")
                if len(page_result[0]) > 1:
                    logger.info(f"First OCR line[1]: {page_result[0][1]}, type: {type(page_result[0][1])}")

            for i, line in enumerate(page_result):
                box = line[0]
                
                if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                    text, score = line[1][0], line[1][1]
                elif isinstance(line[1], (list, tuple)) and len(line[1]) == 1:
                    text = line[1][0]
                    score = 1.0
                else:
                    text = str(line[1])
                    score = 1.0
                
                if i == 0:
                    logger.info(f"Extracted: text='{text}', box={box}, box_type={type(box)}")
                
                extracted_data.append({
                    "text": text,
                    "confidence": score,
                    "box": box
                })
        else:
            logger.error(f"Unknown page_result type: {type(page_result)}")
            return []
            
        logger.info(f"Extracted {len(extracted_data)} text regions")
        return extracted_data

# Singleton instance
ocr_service = OCRService()
