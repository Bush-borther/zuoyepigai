from pathlib import Path
from backend.service.ocr_service import ocr_service
from backend.service.llm_client import llm_client
from backend.service.image_processor import image_processor
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class GradingService:
    def __init__(self):
        self.output_dir = Path("backend/static/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def grade_exam(self, image_path: Path) -> dict:
        """
        Full grading pipeline with spatial segmentation:
        1. OCR 
        2. Detect question regions (by question numbers)
        3. Grade each region with LLM
        4. Draw one mark per region
        5. Generate PDF
        """
        # 1. OCR
        ocr_results = ocr_service.extract_text(image_path)
        logger.info(f"OCR found {len(ocr_results)} text regions")
        
        # 2. Detect question regions by finding question numbers
        question_regions = self._detect_question_regions(ocr_results)
        logger.info(f"Detected {len(question_regions)} question regions")
        
        # 3. Grade each region with LLM
        marks = []
        for i, region in enumerate(question_regions):
            logger.info(f"Grading region {i+1}: {len(region['ocr_items'])} OCR items")
            
            # Ask LLM to grade this specific region
            is_correct = self._grade_region(region['ocr_items'])
            
            # Calculate center of region for mark placement
            center_x = (region['x_min'] + region['x_max']) / 2
            center_y = (region['y_min'] + region['y_max']) / 2
            
            marks.append({
                "type": "correct" if is_correct else "wrong",
                "x": center_x,
                "y": center_y
            })
        
        logger.info(f"Generated {len(marks)} marks for {len(question_regions)} regions")
            
        # 4. Draw Marks
        filename = image_path.name
        marked_image_path = self.output_dir / f"graded_{filename}"
        image_processor.draw_marks(image_path, marks, marked_image_path)
        
        # 5. Generate PDF
        pdf_path = self.output_dir / f"graded_{filename}.pdf"
        self._convert_to_pdf(marked_image_path, pdf_path)
        
        return {
            "original_image": f"/static/uploads/{filename}",
            "graded_image": f"/static/results/graded_{filename}",
            "pdf_url": f"/static/results/graded_{filename}.pdf",
            "details": []
        }
    
    def _detect_question_regions(self, ocr_results):
        """
        Detect question regions by finding question numbers (1, 2, 3, etc.)
        and grouping nearby OCR items into regions.
        """
        import re
        
        # Find question numbers
        question_markers = []
        for item in ocr_results:
            text = item.get('text', '').strip()
            # Match patterns like "1", "1.", "1、", "1)", "(1)"
            # But be more strict: must be 1-2 digits only
            if re.match(r'^[\(]?\d{1,2}[.、\))]?$', text) and len(text) <= 4:
                try:
                    num = int(re.search(r'\d+', text).group())
                    if 1 <= num <= 20:  # More restrictive range for questions
                        box = item.get('box', [])
                        if box and len(box) > 0:
                            # Get Y coordinate (vertical position)
                            y_coords = [p[1] for p in box if isinstance(p, (list, tuple)) and len(p) >= 2]
                            if y_coords:
                                question_markers.append({
                                    'number': num,
                                    'y': sum(y_coords) / len(y_coords),
                                    'text': text,
                                    'item': item
                                })
                except:
                    pass
        
        # Sort by Y coordinate (top to bottom)
        question_markers.sort(key=lambda x: x['y'])
        
        # Filter to keep only sequential numbers starting from 1
        # This removes false positives like page numbers, scores, etc.
        filtered_markers = []
        expected_num = 1
        
        for marker in question_markers:
            if marker['number'] == expected_num:
                filtered_markers.append(marker)
                expected_num += 1
            elif marker['number'] < expected_num:
                # Skip duplicates or out-of-order numbers
                continue
        
        logger.info(f"Found {len(question_markers)} potential markers, filtered to {len(filtered_markers)} sequential: {[q['number'] for q in filtered_markers]}")
        
        # If no sequential markers found, try to use all unique numbers in order
        if len(filtered_markers) == 0 and len(question_markers) > 0:
            # Get unique numbers
            seen_numbers = set()
            for marker in question_markers:
                if marker['number'] not in seen_numbers:
                    filtered_markers.append(marker)
                    seen_numbers.add(marker['number'])
            filtered_markers.sort(key=lambda x: x['number'])
            logger.info(f"Using {len(filtered_markers)} unique markers: {[q['number'] for q in filtered_markers]}")
        
        question_markers = filtered_markers
        
        # If no question markers found, create one region for all content
        if len(question_markers) == 0:
            logger.warning("No question markers found, treating entire page as one region")
            all_y = []
            all_x = []
            for item in ocr_results:
                box = item.get('box', [])
                for p in box:
                    if isinstance(p, (list, tuple)) and len(p) >= 2:
                        all_x.append(p[0])
                        all_y.append(p[1])
            
            return [{
                'number': 1,
                'y_min': min(all_y) if all_y else 0,
                'y_max': max(all_y) if all_y else 1000,
                'x_min': min(all_x) if all_x else 0,
                'x_max': max(all_x) if all_x else 1000,
                'ocr_items': ocr_results
            }]
        
        # Create regions based on question markers
        regions = []
        for i, marker in enumerate(question_markers):
            # Determine region boundaries
            y_start = marker['y']
            y_end = question_markers[i+1]['y'] if i+1 < len(question_markers) else float('inf')
            
            # Collect OCR items in this region
            region_items = []
            x_coords = []
            y_coords = []
            
            for item in ocr_results:
                box = item.get('box', [])
                if box and len(box) > 0:
                    item_y = sum(p[1] for p in box if isinstance(p, (list, tuple)) and len(p) >= 2) / len(box)
                    if y_start <= item_y < y_end:
                        region_items.append(item)
                        for p in box:
                            if isinstance(p, (list, tuple)) and len(p) >= 2:
                                x_coords.append(p[0])
                                y_coords.append(p[1])
            
            if region_items:
                regions.append({
                    'number': marker['number'],
                    'y_min': min(y_coords),
                    'y_max': max(y_coords),
                    'x_min': min(x_coords),
                    'x_max': max(x_coords),
                    'ocr_items': region_items
                })
        
        return regions
    
    def _grade_region(self, ocr_items):
        """
        Grade a single question region using LLM.
        Returns True if correct, False if incorrect.
        """
        if not ocr_items:
            return False
        
        # Use LLM to grade this specific region
        region_text = "\n".join([item.get('text', '') for item in ocr_items])
        
        # Simple prompt for single region grading
        graded = llm_client.grade_text(ocr_items)
        
        if graded and len(graded) > 0:
            # Use majority vote if multiple results
            correct_count = sum(1 for g in graded if g.get('is_correct', False))
            return correct_count > len(graded) / 2
        
        # Default to random if LLM fails
        import random
        return random.choice([True, False])
    
    def _merge_nearby_marks(self, marks, distance_threshold=100):
        """
        Merge marks that are close together into single marks.
        Uses simple clustering based on distance.
        """
        if len(marks) == 0:
            return marks
        
        # Sort marks by y-coordinate (top to bottom)
        sorted_marks = sorted(marks, key=lambda m: m['y'])
        
        merged = []
        current_cluster = [sorted_marks[0]]
        
        for mark in sorted_marks[1:]:
            # Check if this mark is close to the current cluster
            cluster_center_x = sum(m['x'] for m in current_cluster) / len(current_cluster)
            cluster_center_y = sum(m['y'] for m in current_cluster) / len(current_cluster)
            
            distance = ((mark['x'] - cluster_center_x) ** 2 + (mark['y'] - cluster_center_y) ** 2) ** 0.5
            
            if distance < distance_threshold:
                # Add to current cluster
                current_cluster.append(mark)
            else:
                # Finalize current cluster and start new one
                merged.append(self._finalize_cluster(current_cluster))
                current_cluster = [mark]
        
        # Don't forget the last cluster
        if current_cluster:
            merged.append(self._finalize_cluster(current_cluster))
        
        return merged
    
    def _finalize_cluster(self, cluster):
        """
        Convert a cluster of marks into a single mark.
        Use majority vote for correctness, average position.
        """
        avg_x = sum(m['x'] for m in cluster) / len(cluster)
        avg_y = sum(m['y'] for m in cluster) / len(cluster)
        
        # Majority vote for correctness
        correct_count = sum(1 for m in cluster if m['type'] == 'correct')
        is_correct = correct_count > len(cluster) / 2
        
        return {
            "type": "correct" if is_correct else "wrong",
            "x": avg_x,
            "y": avg_y
        }


    def _convert_to_pdf(self, image_path: Path, output_path: Path):
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(output_path, "PDF", resolution=100.0)

grading_service = GradingService()
