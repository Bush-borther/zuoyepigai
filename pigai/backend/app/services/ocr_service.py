from paddleocr import PaddleOCR
import numpy as np

class OCRService:
    def __init__(self):
        # Initialize PaddleOCR
        # use_angle_cls=True enables orientation classification
        # lang='ch' for Chinese/English mixed
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')

    def recognize_text(self, image: np.ndarray) -> str:
        """
        Recognize text from an image array (numpy)
        """
        result = self.ocr.ocr(image, cls=True)
        # result structure: [ [ [box], [text, score] ], ... ]
        # If no text found, result is [None] or simple empty list
        
        if not result or result[0] is None:
            return ""

        texts = []
        for line in result:
             for res in line:
                 text = res[1][0]
                 texts.append(text)
        
        return "\n".join(texts)

ocr_service = OCRService()
