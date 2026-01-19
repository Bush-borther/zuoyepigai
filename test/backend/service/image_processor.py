import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        pass

    def load_image(self, image_path: str | Path) -> np.ndarray:
        """
        Load image from path using OpenCV.
        """
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image at {image_path}")
        return image

    def draw_marks(self, image_path: str | Path, marks: list[dict], output_path: str | Path) -> str:
        """
        Draw marks (check/cross) on the image.
        
        Args:
            image_path: Path to source image
            marks: List of dicts, e.g. [{"type": "correct", "x": 100, "y": 200}, {"type": "wrong", "x": 300, "y": 400}]
            output_path: Path to save marked image
            
        Returns:
            Path to saved image
        """
        # Use Pillow for better drawing quality (anti-aliasing)
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        logger.info(f"Drawing {len(marks)} marks on image")
        
        for i, mark in enumerate(marks):
            x, y = int(mark["x"]), int(mark["y"])
            is_correct = mark["type"] == "correct"
            # Use bright, vivid colors
            color = (0, 255, 0) if is_correct else (255, 0, 0)  # Bright green or red
            
            # Much larger size for visibility
            size = 80
            width = 8
            
            logger.info(f"Mark {i+1}: type={mark['type']}, position=({x}, {y})")
            
            if is_correct:
                # Draw check mark - larger and more visible
                points = [(x - 30, y), (x - 10, y + 30), (x + 40, y - 40)]
                draw.line(points, fill=color, width=width, joint="curve")
            else:
                # Draw cross mark - larger
                draw.line([(x - 30, y - 30), (x + 30, y + 30)], fill=color, width=width)
                draw.line([(x + 30, y - 30), (x - 30, y + 30)], fill=color, width=width)
                
        img.save(output_path)
        logger.info(f"Saved marked image to {output_path}")
        return str(output_path)

image_processor = ImageProcessor()
