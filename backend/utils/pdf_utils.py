from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import markdown
from pathlib import Path

def markdown_to_pdf(markdown_content: str, output_path: str) -> str:
    """Convert markdown content to PDF using ReportLab"""
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
    )
    
    # Parse markdown content
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
            continue
            
        if line.startswith('# '):
            # Main title
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith('## '):
            # Section heading
            story.append(Paragraph(line[3:], heading_style))
        elif line.startswith('---'):
            # Separator
            story.append(Spacer(1, 20))
        else:
            # Regular paragraph
            if line:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    
    return output_path

def generate_report_pdf(report_content: str, output_dir: str, filename: str) -> str:
    """Generate PDF report from markdown content"""
    
    output_path = Path(output_dir) / f"{filename}.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    return markdown_to_pdf(report_content, str(output_path))