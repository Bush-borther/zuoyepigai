import cv2
import numpy as np
import os

class ImageService:
    def __init__(self):
        self.orb = cv2.ORB_create(nfeatures=5000)
        # BFMatcher with Hamming distance
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def align_image(self, template_path: str, target_path: str, save_debug: bool = False) -> np.ndarray:
        """
        Align target image to template image using feature matching.
        """
        template_img = cv2.imread(template_path)
        target_img = cv2.imread(target_path)
        
        if template_img is None:
            raise ValueError(f"Could not load template image: {template_path}")
        if target_img is None:
            raise ValueError(f"Could not load target image: {target_path}")

        # Convert to grayscale
        gray_template = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
        gray_target = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        
        # Detect features
        kp1, des1 = self.orb.detectAndCompute(gray_template, None)
        kp2, des2 = self.orb.detectAndCompute(gray_target, None)
        
        if des1 is None or des2 is None:
             raise ValueError("Could not extract features from images")

        # Match features
        matches = self.matcher.match(des1, des2)
        # Sort by distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Keep top matches (e.g. top 15% or top 500)
        num_good_matches = int(len(matches) * 0.15)
        good_matches = matches[:num_good_matches]
        
        if len(good_matches) < 4:
            raise ValueError("Not enough matches found to align images")

        # Extract location of good matches
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # Find Homography
        # Note: We want to warp target (dst) to match template (src)
        # So we finding transform from dst_pts to src_pts
        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        
        if M is None:
            raise ValueError("Could not calculate homography")

        # Warp image
        h, w, _ = template_img.shape
        aligned_img = cv2.warpPerspective(target_img, M, (w, h))
        
        return aligned_img

    def draw_results(self, image: np.ndarray, regions: list, results: list) -> np.ndarray:
        """
        Draw bounding boxes and visual marks (check/cross) on the image.
        """
        img_copy = image.copy()
        
        # Define colors (BGR)
        green = (0, 180, 0)
        red = (0, 0, 255)
        
        for region in regions:
            r_id = region.get('id')
            x = int(region.get('x'))
            y = int(region.get('y'))
            w = int(region.get('width'))
            h = int(region.get('height'))
            
            # Find result
            res = next((r for r in results if r['region_id'] == r_id), None)
            if not res:
                continue
                
            is_correct = res['is_correct']
            color = green if is_correct else red
            
            # Draw box (thinner line)
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), color, 2)
            
            # Draw symbol (Check or Cross)
            # Position: Center of the box or slightly overlaid
            # Let's verify clearly by drawing a symbol at the right side of the box
            
            # Symbol size based on box height, clamped
            s = min(w, h)
            s = max(20, min(s, 50)) 
            
            # Center of symbol
            cx, cy = x + w - s//2, y + h//2
            
            thickness = 3
            
            if is_correct:
                # Draw Checkmark (√)
                # Points relative to (cx, cy)
                # Start left-mid, go down-right, then up-right
                pts = np.array([
                    [x + w - s + int(0.2*s), y + int(0.6*s)],
                    [x + w - s + int(0.4*s), y + int(0.8*s)],
                    [x + w - s + int(0.9*s), y + int(0.2*s)]
                ], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img_copy, [pts], False, color, thickness)
                
            else:
                # Draw Cross (X)
                # Top-left to bottom-right
                cv2.line(img_copy, 
                         (x + w - s + int(0.2*s), y + int(0.2*s)), 
                         (x + w - s + int(0.8*s), y + int(0.8*s)), 
                         color, thickness)
                # Bottom-left to top-right
                cv2.line(img_copy, 
                         (x + w - s + int(0.2*s), y + int(0.8*s)), 
                         (x + w - s + int(0.8*s), y + int(0.2*s)), 
                         color, thickness)
            
        return img_copy

    def crop_region(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
        return image[y:y+h, x:x+w]
    
    def save_image(self, image: np.ndarray, path: str):
        cv2.imwrite(path, image)

image_service = ImageService()
