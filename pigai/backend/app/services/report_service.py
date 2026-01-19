from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import os
import cv2
from app.models.paper import Paper
from app.models.template import Template
from app.services.image_service import image_service

class ReportService:
    def generate_report(self, paper: Paper, template: Template, output_path: str):
        """
        Generate a PDF report for the graded paper.
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph(f"Grading Report: {template.name}", styles['Title']))
        elements.append(Spacer(1, 12))

        # Summary Info
        summary_data = [
            ["Paper ID", str(paper.id)],
            ["Total Score", str(paper.total_score)],
            ["Status", paper.status],
            ["Date", paper.created_at[:10] if paper.created_at else ""]
        ]
        t = Table(summary_data, colWidths=[100, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # Generate Marked Image
        # Load aligned image
        if paper.aligned_image_path:
             img_path = os.path.join("backend/data", paper.aligned_image_path)
             if not os.path.exists(img_path):
                 # Fallback
                 img_path = os.path.join("backend/data", paper.image_path)
        else:
             img_path = os.path.join("backend/data", paper.image_path)

        if os.path.exists(img_path):
             img = cv2.imread(img_path)
             # Convert results list of dicts (from JSON field)
             # paper.results is already a list of dicts/pydantic maps
             # Need to ensure it's compatible
             marked_img = image_service.draw_results(img, template.regions, paper.results)
             
             # Save temp marked image
             marked_path = img_path.replace(".jpg", "_marked.jpg").replace(".png", "_marked.png")
             # Allow for weird extensions/path issues
             if "_marked" not in marked_path:
                  root, ext = os.path.splitext(img_path)
                  marked_path = f"{root}_marked{ext}"

             cv2.imwrite(marked_path, marked_img)
             
             # Add to PDF
             # Scale to fit A4 width (approx 500 points usable)
             img_aspect = img.shape[1] / img.shape[0]
             disp_width = 450
             disp_height = disp_width / img_aspect
             
             elements.append(ReportLabImage(marked_path, width=disp_width, height=disp_height))
        else:
             elements.append(Paragraph("Error: Image not found.", styles['Normal']))

        elements.append(Spacer(1, 12))
        
        # Detailed Results Table (Optional)
        # elements.append(Paragraph("Detailed Results:", styles['Heading2']))
        # ...

        doc.build(elements)
        return output_path

report_service = ReportService()
