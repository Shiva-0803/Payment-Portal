
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY

def parse_markdown_to_pdf(input_file, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    

    # Define styles
    title_style = styles["Title"]
    h1_style = styles["Heading1"]
    h2_style = styles["Heading2"]
    h3_style = styles["Heading3"]
    body_style = styles["BodyText"]
    body_style.alignment = TA_JUSTIFY
    
    # Custom colors
    h1_style.textColor = colors.darkblue
    
    story = []
    
    # Title Page Helper
    story.append(Spacer(1, 100))
    story.append(Paragraph("<b>Semester Exam Fee Payment Portal</b>", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>A Project Report</b>", styles["Heading2"]))
    story.append(Spacer(1, 200))
    story.append(Paragraph("Submitted by:<br/><b>[Your Name]</b>", styles["Normal"]))
    story.append(PageBreak())

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Regex for bold text **text** -> <b>text</b>
    bold_pattern = re.compile(r'\*\*(.*?)\*\*')
    
    current_list_items = []

    def flush_list():
        if current_list_items:
            t = ListFlowable(current_list_items, bulletType='bullet', start='circle', leftIndent=20)
            story.append(t)
            story.append(Spacer(1, 12))
            current_list_items.clear()

    in_code_block = False
    
    for line in lines:
        line = line.strip()
        
        # Code Block Toggle
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            # Render code line as is
            flush_list()
            # Use non-breaking spaces for indentation if we were smarter, but simple plain text for now
            story.append(Paragraph(line, styles["Code"]))
            continue

        # Skip the manual title block we hardcoded
        if "Semester Exam Fee Payment Portal" in line and line.startswith("# "):
            continue
        if "A Project Report" in line:
            continue

        if not line:
            flush_list()
            continue
            
        # Handle Bold formatting
        line = bold_pattern.sub(r'<b>\1</b>', line)

        if line.startswith('# '): # Main Chapter Heading
            flush_list()
            story.append(PageBreak())
            story.append(Paragraph(line[2:], h1_style))
            story.append(Spacer(1, 24))
        elif line.startswith('## '): # Sub Heading
            flush_list()
            story.append(Paragraph(line[3:], h2_style))
            story.append(Spacer(1, 12))
        elif line.startswith('### '): # Sub-Sub Heading
            flush_list()
            story.append(Paragraph(line[4:], h3_style))
            story.append(Spacer(1, 12))
        elif line.startswith('#### '):
            flush_list()
            story.append(Paragraph(line[5:], h3_style))
            story.append(Spacer(1, 12))
        elif line.startswith('- ') or line.startswith('* '):
            # List Item
            clean_line = line[2:]
            current_list_items.append(ListItem(Paragraph(clean_line, body_style)))
        elif line.startswith('|'):
            # Simple skip for tables (ReportLab table parsing is complex, just skipping or dumping as text for now)
            # Or better, just print it as code style text
            flush_list()
            style = styles["Code"]
            story.append(Paragraph(line, style))
        elif line.startswith('class ') or line.startswith('def ') or line.startswith('    ') or line.startswith('if '):
             # Simple Code heuristic
             flush_list()
             story.append(Paragraph(line, styles["Code"]))
        else:
            flush_list()
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 12))

    flush_list()
    doc.build(story)

    print(f"PDF successfully generated at: {output_file}")

if __name__ == "__main__":
    # Define paths
    # Using the absolute path we know from the previous context
    INPUT_MD = r"C:\Users\shiva sai\.gemini\antigravity\brain\843ce337-f167-49b4-86f3-62266a18a6eb\project_documentation.md"
    OUTPUT_PDF = r"d:\0803\Project_Documentation.pdf"
    
    try:
        parse_markdown_to_pdf(INPUT_MD, OUTPUT_PDF)
    except FileNotFoundError:
        print(f"Error: Could not find input file at {INPUT_MD}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
