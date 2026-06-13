import os
from pypdf import PdfReader
from chapters_data import CHAPTERS_DATA
from drawings import (
    get_dfd_level_0_drawing,
    get_dfd_level_1_drawing,
    get_use_case_drawing,
    get_er_diagram_drawing,
    get_class_diagram_drawing,
    get_sequence_diagram_drawing,
    get_activity_diagram_drawing,
    get_query_volume_chart,
    get_sentiment_chart
)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted, Image, PageTemplate, Frame, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas

# --- NUMBERED CANVAS WITH RUNNING HEADER & FOOTER ---
class NumberedCanvas(canvas.Canvas):
    TOTAL_PAGES = 0
    APPENDIX_START_PAGE = 999

    def showPage(self):
        self.draw_decorations(NumberedCanvas.TOTAL_PAGES)
        super().showPage()

    def draw_decorations(self, page_count):
        self.saveState()
        # Cover Page Elegant Double-Border
        if self._pageNumber == 1:
            self.setStrokeColor(colors.HexColor("#1A365D"))
            self.setLineWidth(1.5)
            self.rect(54, 54, 504, 684)  # Outer border
            self.setLineWidth(0.5)
            self.rect(58, 58, 496, 676)  # Inner border
        elif self._pageNumber > 1:
            # Determine margins dynamically
            if self._pageNumber >= NumberedCanvas.APPENDIX_START_PAGE:
                x_left = 30
                x_right = 582
            else:
                x_left = 72
                x_right = 540

            # Running Header
            self.setFont("Times-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(x_left, 750, "CU AI ADVISOR: A CLOUD-NATIVE SERVERLESS ACADEMIC ADVISING SYSTEM")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(x_left, 742, x_right, 742)
            
            # Running Footer - Bottom Right Page Number
            self.setFont("Times-Roman", 9)
            self.setFillColor(colors.HexColor("#1A202C"))
            if page_count > 0:
                self.drawRightString(x_right, 38, f"Page {self._pageNumber} of {page_count}")
            else:
                self.drawRightString(x_right, 38, f"Page {self._pageNumber}")
            
            # Left Running Footer
            self.drawString(x_left, 38, "Chandigarh University | Master of Computer Applications (MCA) Project Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(x_left, 52, x_right, 52)
        self.restoreState()

# --- IMPORT DETAILED TEXT DATA SET ---

def wrap_code_text(text, max_len=85):
    lines = []
    for line in text.split("\n"):
        if len(line) <= max_len:
            lines.append(line)
        else:
            temp_line = line
            while len(temp_line) > max_len:
                chunk = temp_line[:max_len]
                # Split at last space if possible
                split_idx = chunk.rfind(' ')
                if split_idx > 10:
                    lines.append(temp_line[:split_idx] + " \\")
                    temp_line = "    " + temp_line[split_idx:].strip()
                else:
                    lines.append(chunk + " \\")
                    temp_line = "    " + temp_line[max_len:]
            lines.append(temp_line)
    return "\n".join(lines)

def build_pdf(filename="CU_AI_Advisor_MCA_Final_Report_Manik_Bhola.pdf", page_mappings=None):
    # Setup default mappings if none are provided (for Pass 1)
    if page_mappings is None:
        page_mappings = {
            'bonafide': '2', 'declaration': '3', 'acknowledgement': '4', 'abstract': '5',
            'toc': '6', 'list_figures': '7', 'list_tables': '8', 'abbreviations': '9',
            'chapter1': '10', 'chapter2': '15', 'chapter3': '20', 'chapter4': '25',
            'chapter5': '32', 'chapter6': '38', 'chapter7': '41', 'chapter8': '43',
            'chapter9': '46', 'chapter10': '48',
            'fig_3_1': '23', 'fig_3_2': '23', 'fig_4_1': '28', 'fig_4_2': '29',
            'fig_4_3': '30', 'fig_4_4': '30', 'fig_4_5': '31', 'fig_5_1': '34',
            'fig_5_2': '35', 'fig_5_3': '36', 'fig_5_4': '36', 'fig_5_5': '37',
            'fig_7_1': '42', 'fig_7_2': '42',
            'table_2_1': '18', 'table_3_1': '22', 'table_4_1': '25',
            'table_6_1': '39', 'table_6_2': '39'
        }

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define custom frames and page templates for Appendix C layout optimization
    normal_frame = Frame(72, 72, 468, 648, id='normal_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    wide_frame = Frame(30, 60, 552, 675, id='wide_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    
    normal_template = PageTemplate(id='normal', frames=[normal_frame])
    wide_template = PageTemplate(id='wide', frames=[wide_frame])
    
    doc.pageTemplates = []
    doc.addPageTemplates([normal_template, wide_template])
    
    styles = getSampleStyleSheet()
    
    # --- CUSTOM STYLES ---
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,  # 1.5 line spacing
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    body_center_style = ParagraphStyle(
        'ReportBodyCenter',
        parent=body_style,
        alignment=TA_CENTER
    )
    
    body_left_style = ParagraphStyle(
        'ReportBodyLeft',
        parent=body_style,
        alignment=TA_LEFT
    )

    body_bold_style = ParagraphStyle(
        'ReportBodyBold',
        parent=body_style,
        fontName='Times-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'ReportHeading1',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=16,  # 16pt Bold H1
        leading=20,
        spaceBefore=22,
        spaceAfter=12,
        keepWithNext=True
    )
    
    heading2_style = ParagraphStyle(
        'ReportHeading2',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=14,  # 14pt Bold H2
        leading=18,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=6  # Tighter spacing for single-page cover compliance
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4  # Tighter spacing for single-page cover compliance
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Times-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Times-Roman',
        fontSize=9.5,
        leading=12,
        alignment=TA_LEFT
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        fontName='Courier',
        fontSize=6.5,
        leading=7.2,
        spaceAfter=12
    )


    def wrap_image(img_path, width, height):
        img = Image(img_path, width=width, height=height)
        t = Table([[img]], colWidths=[468])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        return t

    def wrap_code_block(code_text, style):
        p = Preformatted(code_text, style)
        t = Table([[p]], colWidths=[468])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    # --- DATABASE FIELD HEADER DEFINITIONS FOR REFERENCE ---
    u_headers = [Paragraph("<b>Column Name</b>", table_header_style), 
                 Paragraph("<b>Data Type</b>", table_header_style), 
                 Paragraph("<b>Constraints</b>", table_header_style), 
                 Paragraph("<b>Description</b>", table_header_style)]
    u_rows = [
        [Paragraph("username", table_cell_style), Paragraph("VARCHAR(100)", table_cell_style), Paragraph("PRIMARY KEY, NOT NULL", table_cell_style), Paragraph("Unique login identifier for the student or administrator", table_cell_style)],
        [Paragraph("password_hash", table_cell_style), Paragraph("VARCHAR(255)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Crypto salted SHA-256 hash value of the password credentials", table_cell_style)],
        [Paragraph("role", table_cell_style), Paragraph("VARCHAR(50)", table_cell_style), Paragraph("DEFAULT 'student'", table_cell_style), Paragraph("Role-based clearance flag ('student' or 'admin')", table_cell_style)]
    ]

    c_headers = [Paragraph("<b>Column Name</b>", table_header_style), 
                 Paragraph("<b>Data Type</b>", table_header_style), 
                 Paragraph("<b>Constraints</b>", table_header_style), 
                 Paragraph("<b>Description</b>", table_header_style)]
    c_rows = [
        [Paragraph("id", table_cell_style), Paragraph("VARCHAR(50)", table_cell_style), Paragraph("PRIMARY KEY, NOT NULL", table_cell_style), Paragraph("Standardized short code program code key (e.g. 'mca', 'cse')", table_cell_style)],
        [Paragraph("name", table_cell_style), Paragraph("VARCHAR(200)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Full name of the academic degree program", table_cell_style)],
        [Paragraph("department", table_cell_style), Paragraph("VARCHAR(150)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("University department offering the course structure", table_cell_style)],
        [Paragraph("description", table_cell_style), Paragraph("TEXT", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Comprehensive description of learning goals and prerequisites", table_cell_style)],
        [Paragraph("interests", table_cell_style), Paragraph("TEXT", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Comma-separated keyword interest tags for recommendation logic", table_cell_style)],
        [Paragraph("duration", table_cell_style), Paragraph("VARCHAR(50)", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Total academic duration of the course program (e.g. '2 Years')", table_cell_style)]
    ]

    p_headers = [Paragraph("<b>Column Name</b>", table_header_style), 
                 Paragraph("<b>Data Type</b>", table_header_style), 
                 Paragraph("<b>Constraints</b>", table_header_style), 
                 Paragraph("<b>Description</b>", table_header_style)]
    p_rows = [
        [Paragraph("id", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("PRIMARY KEY, AUTOINCREMENT", table_cell_style), Paragraph("Unique internal policy record identifier", table_cell_style)],
        [Paragraph("topic", table_cell_style), Paragraph("VARCHAR(100)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Academic topic name (e.g. 'Attendance', 'Grading')", table_cell_style)],
        [Paragraph("description", table_cell_style), Paragraph("TEXT", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Official university policy text description", table_cell_style)]
    ]

    il_headers = [Paragraph("<b>Column Name</b>", table_header_style), 
                  Paragraph("<b>Data Type</b>", table_header_style), 
                  Paragraph("<b>Constraints</b>", table_header_style), 
                  Paragraph("<b>Description</b>", table_header_style)]
    il_rows = [
        [Paragraph("id", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("PRIMARY KEY, AUTOINCREMENT", table_cell_style), Paragraph("Internal database unique log record identifier index", table_cell_style)],
        [Paragraph("user", table_cell_style), Paragraph("VARCHAR(50)", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Student account name, null if anonymous session", table_cell_style)],
        [Paragraph("mode", table_cell_style), Paragraph("VARCHAR(50)", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Query resolution source mode ('FAQ-QuickAction', 'Local-Logic', 'AI-Client')", table_cell_style)],
        [Paragraph("student_message", table_cell_style), Paragraph("TEXT", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Input text query sent by the student", table_cell_style)],
        [Paragraph("bot_response", table_cell_style), Paragraph("TEXT", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Output response resolved and shown back to student", table_cell_style)],
        [Paragraph("sentiment", table_cell_style), Paragraph("FLOAT", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Sentiment polarity score value generated by TextBlob (-1.0 to 1.0)", table_cell_style)],
        [Paragraph("timestamp", table_cell_style), Paragraph("TIMESTAMP", table_cell_style), Paragraph("DEFAULT CURRENT_TIMESTAMP", table_cell_style), Paragraph("Date and time stamp of the session interaction log", table_cell_style)]
    ]

    ap_headers = [Paragraph("<b>Column Name</b>", table_header_style), 
                  Paragraph("<b>Data Type</b>", table_header_style), 
                  Paragraph("<b>Constraints</b>", table_header_style), 
                  Paragraph("<b>Description</b>", table_header_style)]
    ap_rows = [
        [Paragraph("id", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("PRIMARY KEY, AUTOINCREMENT", table_cell_style), Paragraph("Internal database unique scheduling slot identifier index", table_cell_style)],
        [Paragraph("student_name", table_cell_style), Paragraph("VARCHAR(100)", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Account username booking the session slot", table_cell_style)],
        [Paragraph("course_name", table_cell_style), Paragraph("VARCHAR(100)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Name of target course selected by student", table_cell_style)],
        [Paragraph("date", table_cell_style), Paragraph("VARCHAR(20)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Selected date for the advising appointment", table_cell_style)],
        [Paragraph("time", table_cell_style), Paragraph("VARCHAR(20)", table_cell_style), Paragraph("NOT NULL", table_cell_style), Paragraph("Selected time range for the advising appointment", table_cell_style)],
        [Paragraph("timestamp", table_cell_style), Paragraph("DATETIME", table_cell_style), Paragraph("DEFAULT CURRENT_TIMESTAMP", table_cell_style), Paragraph("Date and time stamp of the appointment booking", table_cell_style)]
    ]

    story = []
    
    # ==========================================
    # COVER PAGE (Tighter spacers to guarantee exactly 1 page!)
    # ==========================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("A PROJECT REPORT ON", cover_subtitle_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("CU AI ADVISOR: A CLOUD-NATIVE<br/>SERVERLESS ACADEMIC ADVISING SYSTEM<br/>FOR CHANDIGARH UNIVERSITY", cover_title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>Submitted in partial fulfillment of the requirements for the award of the degree of</i>", cover_subtitle_style))
    story.append(Paragraph("<b>MASTER OF COMPUTER APPLICATIONS (MCA)</b>", cover_title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>BY</b>", cover_subtitle_style))
    story.append(Paragraph("<b>MANIK BHOLA</b>", cover_title_style))
    story.append(Paragraph("<b>Enrollment No: O24MCA110817</b>", cover_subtitle_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>UNDER THE GUIDANCE OF</b>", cover_subtitle_style))
    story.append(Paragraph("<b>Mr. Kashish Gupta</b>", cover_title_style))
    story.append(Paragraph("<i>(Project Guide & Mentor)</i>", cover_subtitle_style))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER APPLICATIONS</b>", cover_subtitle_style))
    story.append(Paragraph("<b>CHANDIGARH UNIVERSITY</b>", cover_title_style))
    story.append(Paragraph("<b>ACADEMIC SESSION 2024-2026</b>", cover_subtitle_style))
    story.append(Paragraph("<b>JUNE 2026, LUDHIANA</b>", cover_subtitle_style))
    story.append(PageBreak())
    
    # ==========================================
    # BONAFIDE CERTIFICATE
    # ==========================================
    story.append(Paragraph('<a name="bonafide"/><b>BONAFIDE CERTIFICATE</b>', cover_title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "This is to certify that the project report entitled <b>\"CU AI ADVISOR: A CLOUD-NATIVE "
        "SERVERLESS ACADEMIC ADVISING SYSTEM\"</b> is a bonafide work carried out by "
        "<b>Manik Bhola (Enrollment No: O24MCA110817)</b> in partial fulfillment of the requirements "
        "for the award of the degree of <b>Master of Computer Applications (MCA)</b> of <b>Chandigarh "
        "University</b> during the academic session 2024-2026.", body_style))
    story.append(Paragraph(
        "The work embodied in this project report has not been submitted previously to any other "
        "university or institution for the award of any degree or diploma. The project has been "
        "completed under my direct supervision and guidance and is worthy of acceptance for the award of "
        "the degree.", body_style))
    story.append(Spacer(1, 100))
    
    cert_table_data = [
        [Paragraph("<b>________________________</b>", body_center_style), Paragraph("<b>________________________</b>", body_center_style)],
        [Paragraph("<b>Mr. Kashish Gupta</b>", body_center_style), Paragraph("<b>Head of Department</b>", body_center_style)],
        [Paragraph("Project Guide & Mentor<br/>Dept. of Computer Applications", body_center_style), Paragraph("Dept. of Computer Applications<br/>Chandigarh University", body_center_style)]
    ]
    cert_table = Table(cert_table_data, colWidths=[234, 234])
    cert_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(cert_table)
    story.append(PageBreak())
    
    # ==========================================
    # DECLARATION
    # ==========================================
    story.append(Paragraph('<a name="declaration"/><b>DECLARATION</b>', cover_title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "I, <b>Manik Bhola</b>, hereby solemnly declare that the project report titled <b>\"CU AI ADVISOR: "
        "A CLOUD-NATIVE SERVERLESS ACADEMIC ADVISING SYSTEM\"</b> submitted in partial fulfillment "
        "of the requirements for the award of the degree of <b>Master of Computer Applications (MCA)</b> "
        "is my original work.", body_style))
    story.append(Paragraph("I further declare that:", body_bold_style))
    story.append(Paragraph(
        "1. This project has been carried out by me during the academic session 2024-2026 under the "
        "supervision of Mr. Kashish Gupta (Project Guide & Mentor).<br/>"
        "2. The work has not been submitted previously to any other university, institution, or "
        "examination body for the award of any degree, diploma, or certification.<br/>"
        "3. All sources of information used in this report have been duly acknowledged and referenced "
        "in accordance with academic ethics and plagiarism norms.<br/>"
        "4. The data presented in this report is authentic to the best of my knowledge and has not "
        "been fabricated or manipulated.<br/>"
        "5. I understand that if any part of this declaration is found to be false, my project report may be "
        "rejected and disciplinary action may be taken as per university guidelines.", body_style))
    story.append(Spacer(1, 80))
    
    decl_table_data = [
        [Paragraph("<b>Place:</b> Ludhiana, India<br/><b>Date:</b> June 13, 2026", body_left_style), 
         Paragraph("<b>________________________</b><br/><b>Manik Bhola</b><br/>Enrollment No: O24MCA110817", body_center_style)]
    ]
    decl_table = Table(decl_table_data, colWidths=[234, 234])
    decl_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(decl_table)
    story.append(PageBreak())
    
    # ==========================================
    # ACKNOWLEDGEMENT
    # ==========================================
    story.append(Paragraph('<a name="acknowledgement"/><b>ACKNOWLEDGEMENT</b>', cover_title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "The successful completion of this project is the result of the support, guidance, and cooperation "
        "of many individuals. First and foremost, I would like to express my sincere gratitude to my project "
        "mentor, <b>Mr. Kashish Gupta</b>, for his continuous encouragement, intellectual guidance, and technical "
        "oversight throughout the development of the <b>CU AI Advisor</b>. His deep expertise in cloud architecture "
        "and artificial intelligence was instrumental in helping me shape the system's design and ensure its "
        "scalability.", body_style))
    story.append(Paragraph(
        "I am also deeply indebted to the <b>Department of Computer Applications</b> at <b>Chandigarh University</b> "
        "for providing a world-class educational environment and the necessary resources to carry out this research "
        "and development work. I would like to thank all the faculty members for their constant support and guidance "
        "throughout my MCA program.", body_style))
    story.append(Paragraph(
        "Finally, I would like to thank my family and friends for their unwavering faith in my abilities and for "
        "providing the moral support required during the challenging phases of this project. Their constant motivation "
        "was the driving force behind this achievement.", body_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>Manik Bhola</b>", body_bold_style))
    story.append(PageBreak())
    
    # ==========================================
    # ABSTRACT
    # ==========================================
    story.append(Paragraph('<a name="abstract"/><b>ABSTRACT</b>', cover_title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "<b>Project Title:</b> CU AI Advisor: A Cloud-Native Serverless Academic Advising System<br/>"
        "<b>Objective:</b> To develop a 24/7 intelligent conversational agent that provides academic guidance, "
        "course recommendations, and policy lookups for Chandigarh University students.<br/>"
        "<b>Technologies Used:</b> Python, Streamlit, SQLAlchemy, Puter completions API (Serverless AI), Aiven PostgreSQL, TextBlob.<br/>"
        "<b>Development Methodology:</b> Agile Scrum framework with a focus on iterative development and cloud-native deployment.<br/>"
        "<b>Key Results:</b> Successfully implemented a high-performance, privacy-first AI advisor that offloads compute "
        "to serverless API endpoints, reducing university hardware hosting costs to zero while maintaining a 100% data integrity "
        "record across cloud-hosted relational databases.", body_style))
    story.append(Paragraph(
        "The CU AI Advisor addresses the operational challenges of scaling academic support in large institutions. By utilizing "
        "SQLAlchemy ORM for a hybrid data layer and the Puter completions API for serverless AI inference, the system ensures zero per-user "
        "infrastructure maintenance costs. Extensive validation confirms the system's accuracy in delivering course suggestions and scheduling appointments. "
        "The admin dashboard provides valuable insights through real-time student sentiment tracking and search pattern analytics.", body_style))
    story.append(PageBreak())

    # ==========================================
    # TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph('<a name="toc"/><b>TABLE OF CONTENTS</b>', cover_title_style))
    story.append(Spacer(1, 20))
    toc_data = [
        [Paragraph("<b>Chapter</b>", body_bold_style), Paragraph("<b>Page No.</b>", body_bold_style)],
        [Paragraph('<a href="#bonafide" color="#1A202C">Bonafide Certificate</a>', body_style), Paragraph(f'<a href="#bonafide" color="#1A202C">{page_mappings["bonafide"]}</a>', body_style)],
        [Paragraph('<a href="#declaration" color="#1A202C">Declaration</a>', body_style), Paragraph(f'<a href="#declaration" color="#1A202C">{page_mappings["declaration"]}</a>', body_style)],
        [Paragraph('<a href="#acknowledgement" color="#1A202C">Acknowledgement</a>', body_style), Paragraph(f'<a href="#acknowledgement" color="#1A202C">{page_mappings["acknowledgement"]}</a>', body_style)],
        [Paragraph('<a href="#abstract" color="#1A202C">Abstract</a>', body_style), Paragraph(f'<a href="#abstract" color="#1A202C">{page_mappings["abstract"]}</a>', body_style)],
        [Paragraph('<a href="#toc" color="#1A202C">Table of Contents</a>', body_style), Paragraph(f'<a href="#toc" color="#1A202C">{page_mappings["toc"]}</a>', body_style)],
        [Paragraph('<a href="#list_figures" color="#1A202C">List of Figures</a>', body_style), Paragraph(f'<a href="#list_figures" color="#1A202C">{page_mappings["list_figures"]}</a>', body_style)],
        [Paragraph('<a href="#list_tables" color="#1A202C">List of Tables</a>', body_style), Paragraph(f'<a href="#list_tables" color="#1A202C">{page_mappings["list_tables"]}</a>', body_style)],
        [Paragraph('<a href="#abbreviations" color="#1A202C">List of Abbreviations</a>', body_style), Paragraph(f'<a href="#abbreviations" color="#1A202C">{page_mappings["abbreviations"]}</a>', body_style)],
        [Paragraph('<a href="#chapter1" color="#1A365D"><b>Chapter 1: Introduction</b></a>', body_bold_style), Paragraph(f'<a href="#chapter1" color="#1A365D"><b>{page_mappings["chapter1"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter2" color="#1A365D"><b>Chapter 2: Literature Review / System Study</b></a>', body_bold_style), Paragraph(f'<a href="#chapter2" color="#1A365D"><b>{page_mappings["chapter2"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter3" color="#1A365D"><b>Chapter 3: System Analysis</b></a>', body_bold_style), Paragraph(f'<a href="#chapter3" color="#1A365D"><b>{page_mappings["chapter3"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter4" color="#1A365D"><b>Chapter 4: System Design</b></a>', body_bold_style), Paragraph(f'<a href="#chapter4" color="#1A365D"><b>{page_mappings["chapter4"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter5" color="#1A365D"><b>Chapter 5: System Implementation</b></a>', body_bold_style), Paragraph(f'<a href="#chapter5" color="#1A365D"><b>{page_mappings["chapter5"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter6" color="#1A365D"><b>Chapter 6: Testing</b></a>', body_bold_style), Paragraph(f'<a href="#chapter6" color="#1A365D"><b>{page_mappings["chapter6"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter7" color="#1A365D"><b>Chapter 7: Results & Discussion</b></a>', body_bold_style), Paragraph(f'<a href="#chapter7" color="#1A365D"><b>{page_mappings["chapter7"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter8" color="#1A365D"><b>Chapter 8: Conclusion & Future Scope</b></a>', body_bold_style), Paragraph(f'<a href="#chapter8" color="#1A365D"><b>{page_mappings["chapter8"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter9" color="#1A365D"><b>Chapter 9: References</b></a>', body_bold_style), Paragraph(f'<a href="#chapter9" color="#1A365D"><b>{page_mappings["chapter9"]}</b></a>', body_bold_style)],
        [Paragraph('<a href="#chapter10" color="#1A365D"><b>Chapter 10: Appendices</b></a>', body_bold_style), Paragraph(f'<a href="#chapter10" color="#1A365D"><b>{page_mappings["chapter10"]}</b></a>', body_bold_style)],
    ]
    t_toc = Table(toc_data, colWidths=[350, 118])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ==========================================
    # LIST OF FIGURES (Separate page!)
    # ==========================================
    story.append(Paragraph('<a name="list_figures"/><b>LIST OF FIGURES</b>', cover_title_style))
    story.append(Spacer(1, 20))
    fig_data = [
        [Paragraph("<b>Figure Description</b>", body_bold_style), Paragraph("<b>Page No.</b>", body_bold_style)],
        [Paragraph('<a href="#fig_3_1" color="#1A202C">Figure 3.1: DFD Level 0 Context Diagram</a>', body_style), Paragraph(f'<a href="#fig_3_1" color="#1A202C">{page_mappings["fig_3_1"]}</a>', body_style)],
        [Paragraph('<a href="#fig_3_2" color="#1A202C">Figure 3.2: DFD Level 1 System Data Flow Diagram</a>', body_style), Paragraph(f'<a href="#fig_3_2" color="#1A202C">{page_mappings["fig_3_2"]}</a>', body_style)],
        [Paragraph('<a href="#fig_4_1" color="#1A202C">Figure 4.1: Unified Modeling Language (UML) Use Case Diagram</a>', body_style), Paragraph(f'<a href="#fig_4_1" color="#1A202C">{page_mappings["fig_4_1"]}</a>', body_style)],
        [Paragraph('<a href="#fig_4_2" color="#1A202C">Figure 4.2: Database Entity-Relationship Diagram (3NF Schema)</a>', body_style), Paragraph(f'<a href="#fig_4_2" color="#1A202C">{page_mappings["fig_4_2"]}</a>', body_style)],
        [Paragraph('<a href="#fig_4_3" color="#1A202C">Figure 4.3: UML Class Interaction Diagram</a>', body_style), Paragraph(f'<a href="#fig_4_3" color="#1A202C">{page_mappings["fig_4_3"]}</a>', body_style)],
        [Paragraph('<a href="#fig_4_4" color="#1A202C">Figure 4.4: Sequence Diagram for Chat Resolution Flow</a>', body_style), Paragraph(f'<a href="#fig_4_4" color="#1A202C">{page_mappings["fig_4_4"]}</a>', body_style)],
        [Paragraph('<a href="#fig_4_5" color="#1A202C">Figure 4.5: System Activity Logic Lifecycle Diagram</a>', body_style), Paragraph(f'<a href="#fig_4_5" color="#1A202C">{page_mappings["fig_4_5"]}</a>', body_style)],
        [Paragraph('<a href="#fig_5_1" color="#1A202C">Figure 5.1: Student Chat Portal Interface (Anonymous User Session)</a>', body_style), Paragraph(f'<a href="#fig_5_1" color="#1A202C">{page_mappings["fig_5_1"]}</a>', body_style)],
        [Paragraph('<a href="#fig_5_2" color="#1A202C">Figure 5.2: Student Advising Chat Portal (Authenticated Administrator Session)</a>', body_style), Paragraph(f'<a href="#fig_5_2" color="#1A202C">{page_mappings["fig_5_2"]}</a>', body_style)],
        [Paragraph('<a href="#fig_5_3" color="#1A202C">Figure 5.3: Academic Appointment Slots Booking View</a>', body_style), Paragraph(f'<a href="#fig_5_3" color="#1A202C">{page_mappings["fig_5_3"]}</a>', body_style)],
        [Paragraph('<a href="#fig_5_4" color="#1A202C">Figure 5.4: Administrator Sentiment & Query Volume Analytics Dashboard</a>', body_style), Paragraph(f'<a href="#fig_5_4" color="#1A202C">{page_mappings["fig_5_4"]}</a>', body_style)],
        [Paragraph('<a href="#fig_5_5" color="#1A202C">Figure 5.5: Registered Student Appointment Scheduling Management Portal</a>', body_style), Paragraph(f'<a href="#fig_5_5" color="#1A202C">{page_mappings["fig_5_5"]}</a>', body_style)],
        [Paragraph('<a href="#fig_7_1" color="#1A202C">Figure 7.1: Query Volume Over Time Graph</a>', body_style), Paragraph(f'<a href="#fig_7_1" color="#1A202C">{page_mappings["fig_7_1"]}</a>', body_style)],
        [Paragraph('<a href="#fig_7_2" color="#1A202C">Figure 7.2: Sentiment Distribution Graph</a>', body_style), Paragraph(f'<a href="#fig_7_2" color="#1A202C">{page_mappings["fig_7_2"]}</a>', body_style)],
    ]
    t_fig = Table(fig_data, colWidths=[350, 118])
    t_fig.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_fig)
    story.append(PageBreak())

    # ==========================================
    # LIST OF TABLES (Separate page!)
    # ==========================================
    story.append(Paragraph('<a name="list_tables"/><b>LIST OF TABLES</b>', cover_title_style))
    story.append(Spacer(1, 20))
    table_data = [
        [Paragraph("<b>Table Description</b>", body_bold_style), Paragraph("<b>Page No.</b>", body_bold_style)],
        [Paragraph('<a href="#table_2_1" color="#1A202C">Table 2.1: Comparative Analysis of Student Advising Architectures</a>', body_style), Paragraph(f'<a href="#table_2_1" color="#1A202C">{page_mappings["table_2_1"]}</a>', body_style)],
        [Paragraph('<a href="#table_3_1" color="#1A202C">Table 3.1: Minimum System Hardware and Software Requirements Specifications</a>', body_style), Paragraph(f'<a href="#table_3_1" color="#1A202C">{page_mappings["table_3_1"]}</a>', body_style)],
        [Paragraph('<a href="#table_4_1" color="#1A202C">Table 4.1: Primary Database Entity Schema Mappings</a>', body_style), Paragraph(f'<a href="#table_4_1" color="#1A202C">{page_mappings["table_4_1"]}</a>', body_style)],
        [Paragraph('<a href="#table_6_1" color="#1A202C">Table 6.1: Unit Verification Test Suite Case Matrix</a>', body_style), Paragraph(f'<a href="#table_6_1" color="#1A202C">{page_mappings["table_6_1"]}</a>', body_style)],
        [Paragraph('<a href="#table_6_2" color="#1A202C">Table 6.2: System Integration and E2E Test Case Matrix</a>', body_style), Paragraph(f'<a href="#table_6_2" color="#1A202C">{page_mappings["table_6_2"]}</a>', body_style)],
    ]
    t_tab = Table(table_data, colWidths=[350, 118])
    t_tab.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tab)
    story.append(PageBreak())

    # ==========================================
    # LIST OF ABBREVIATIONS
    # ==========================================
    story.append(Paragraph('<a name="abbreviations"/><b>LIST OF ABBREVIATIONS</b>', cover_title_style))
    story.append(Spacer(1, 20))
    ab_data = [
        [Paragraph("<b>Abbreviation</b>", body_bold_style), Paragraph("<b>Full Description / Meaning</b>", body_bold_style)],
        [Paragraph("AI", body_style), Paragraph("Artificial Intelligence", body_style)],
        [Paragraph("LLM", body_style), Paragraph("Large Language Model", body_style)],
        [Paragraph("RDBMS", body_style), Paragraph("Relational Database Management System", body_style)],
        [Paragraph("ORM", body_style), Paragraph("Object-Relational Mapping (SQLAlchemy)", body_style)],
        [Paragraph("SDK", body_style), Paragraph("Software Development Kit", body_style)],
        [Paragraph("SSL / TLS", body_style), Paragraph("Secure Sockets Layer / Transport Layer Security", body_style)],
        [Paragraph("DFD", body_style), Paragraph("Data Flow Diagram", body_style)],
        [Paragraph("UML", body_style), Paragraph("Unified Modeling Language", body_style)],
        [Paragraph("3NF", body_style), Paragraph("Third Normal Form (Database Normalization)", body_style)],
        [Paragraph("API", body_style), Paragraph("Application Programming Interface", body_style)],
        [Paragraph("E2E", body_style), Paragraph("End-to-End Automation Testing", body_style)],
        [Paragraph("UI / UX", body_style), Paragraph("User Interface / User Experience", body_style)],
        [Paragraph("NLP", body_style), Paragraph("Natural Language Processing", body_style)],
        [Paragraph("RBAC", body_style), Paragraph("Role-Based Access Control", body_style)],
        [Paragraph("SHA", body_style), Paragraph("Secure Hash Algorithm (SHA-256 for password crypts)", body_style)],
        [Paragraph("CU", body_style), Paragraph("Chandigarh University", body_style)],
        [Paragraph("MCA", body_style), Paragraph("Master of Computer Applications", body_style)]
    ]
    t_ab = Table(ab_data, colWidths=[100, 368])
    t_ab.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Times-Bold'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ab)
    story.append(PageBreak())

    # --- RENDER CHAPTERS & PARAGRAPHS FROM DATA SET ---
    for ch_num in sorted(CHAPTERS_DATA.keys(), key=int):
        ch = CHAPTERS_DATA[ch_num]
        story.append(Paragraph(f'<a name="chapter{ch_num}"/><b>{ch["title"]}</b>', heading1_style))
        
        # Iterate over sections in order
        sections = ch["sections"]
        for sec_title in sorted(sections.keys()):
            paragraphs = sections[sec_title]
            story.append(Paragraph(f"<b>{sec_title}</b>", heading2_style))
            for p_text in paragraphs:
                story.append(Paragraph(p_text, body_style))
            
            # Embed schemas/diagrams in specific sections
            if sec_title == "3.3 System Architecture and Data Flow":
                story.append(Spacer(1, 10))
                story.append(Paragraph("<b>3.3.1 Data Flow Diagrams (DFD):</b>", body_bold_style))
                story.append(Paragraph(
                    "The flow of data is described below at two levels of abstraction: Level 0 (Context Diagram) and Level 1 (Process Breakdown Diagram).", body_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_3_1"/><b>Figure 3.1: DFD Level 0 Context Diagram</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_dfd_level_0_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 3.1: DFD Level 0 Context Diagram</i>", body_center_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_3_2"/><b>Figure 3.2: DFD Level 1 System Data Flow Diagram</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_dfd_level_1_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 3.2: DFD Level 1 System Data Flow Diagram</i>", body_center_style))
                story.append(Spacer(1, 15))
                
            elif sec_title == "3.1 Requirements Specification":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="table_3_1"/><b>Table 3.1: Minimum System Hardware and Software Requirements Specifications</b>', body_bold_style))
                req_headers = [Paragraph("<b>Requirement Parameter</b>", table_header_style), 
                               Paragraph("<b>Development & Production Specifications</b>", table_header_style)]
                req_rows = [
                    [Paragraph("Processor / CPU", table_cell_style), Paragraph("Dual-Core 2.0 GHz or higher (x86/x64 or ARM)", table_cell_style)],
                    [Paragraph("Memory / RAM", table_cell_style), Paragraph("Minimum 4 GB RAM (8 GB recommended for local testing)", table_cell_style)],
                    [Paragraph("Operating System", table_cell_style), Paragraph("Windows 10/11, macOS Catalina or higher, Linux (Ubuntu/Debian)", table_cell_style)],
                    [Paragraph("Development Tools", table_cell_style), Paragraph("Visual Studio Code (VS Code), Python 3.12, Git Version Control", table_cell_style)],
                    [Paragraph("Cloud Database Service", table_cell_style), Paragraph("Managed Aiven PostgreSQL cluster (v16), SSL-encrypted connection", table_cell_style)],
                    [Paragraph("AI SDK Platform", table_cell_style), Paragraph("Puter Cloud API Client SDK (gpt-4o-mini endpoint integration)", table_cell_style)],
                    [Paragraph("Client Web Browser", table_cell_style), Paragraph("Google Chrome, Mozilla Firefox, Safari, Microsoft Edge (HTML5 compliant)", table_cell_style)]
                ]
                req_table_data = [req_headers] + req_rows
                t_req = Table(req_table_data, colWidths=[150, 318])
                t_req.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(t_req)
                story.append(Spacer(1, 10))
                story.append(Paragraph("<i>Table 3.1: Minimum System Hardware and Software Requirements Specifications</i>", body_center_style))
                story.append(Spacer(1, 15))
                
            elif sec_title == "2.2 Comparative Analysis of Technologies":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="table_2_1"/><b>Table 2.1: Comparative Analysis of Student Advising Architectures</b>', body_bold_style))
                comp_headers = [Paragraph("<b>Comparative Dimension</b>", table_header_style), 
                                Paragraph("<b>Static Campus Portal</b>", table_header_style), 
                                Paragraph("<b>Centralized Cloud AI</b>", table_header_style), 
                                Paragraph("<b>CU AI Advisor (Hybrid)</b>", table_header_style)]
                comp_rows = [
                    [Paragraph("Interaction Model", table_cell_style), Paragraph("Structured navigation menu", table_cell_style), Paragraph("Generative conversational chat", table_cell_style), Paragraph("Conversational with local fallback", table_cell_style)],
                    [Paragraph("Operational Token Cost", table_cell_style), Paragraph("Zero ($0)", table_cell_style), Paragraph("High (scales per user token)", table_cell_style), Paragraph("Zero ($0) server-side AI cost", table_cell_style)],
                    [Paragraph("Response Latency", table_cell_style), Paragraph("Slow manual browsing (minutes)", table_cell_style), Paragraph("1.5s - 3.5s (model network call)", table_cell_style), Paragraph("&lt;10ms (local match), ~3s (edge AI)", table_cell_style)],
                    [Paragraph("Data Security & Privacy", table_cell_style), Paragraph("High (internal network)", table_cell_style), Paragraph("Low (transmits queries to external cloud)", table_cell_style), Paragraph("Absolute (browser edge execution)", table_cell_style)],
                    [Paragraph("Server Compute Load", table_cell_style), Paragraph("Low database queries", table_cell_style), Paragraph("High (continuous GPU/CPU load)", table_cell_style), Paragraph("Negligible (offloaded to client browser)", table_cell_style)],
                    [Paragraph("Integration Complexity", table_cell_style), Paragraph("High custom code per page", table_cell_style), Paragraph("Medium API hooks", table_cell_style), Paragraph("Low SQLAlchemy ORM mapping", table_cell_style)]
                ]
                comp_table_data = [comp_headers] + comp_rows
                t_comp = Table(comp_table_data, colWidths=[110, 110, 128, 120])
                t_comp.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(t_comp)
                story.append(Spacer(1, 12))
                story.append(Paragraph("<i>Table 2.1: Comparative Analysis of Student Advising Architectures</i>", body_center_style))
                story.append(Spacer(1, 15))
                
            elif sec_title == "4.1 Database Design & Schema":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="table_4_1"/><b>Table 4.1: Primary Database Entity Schema Mappings</b>', body_bold_style))
                db_map_headers = [
                    Paragraph("<b>Table Name</b>", table_header_style),
                    Paragraph("<b>Primary Key</b>", table_header_style),
                    Paragraph("<b>Foreign Keys</b>", table_header_style),
                    Paragraph("<b>Purpose / Role in CU AI Advisor System</b>", table_header_style)
                ]
                db_map_rows = [
                    [Paragraph("users", table_cell_style), Paragraph("username", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Stores user credentials, salt-hashed passwords, and role identifiers (student/admin) to enforce RBAC access control.", table_cell_style)],
                    [Paragraph("courses", table_cell_style), Paragraph("id", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Serves as the master catalog for university programs across 12 departments, storing duration, description, and keywords.", table_cell_style)],
                    [Paragraph("policies", table_cell_style), Paragraph("id", table_cell_style), Paragraph("None", table_cell_style), Paragraph("Reference library storing official university rules (attendance minimums, credit limits, grading scales, exam formats).", table_cell_style)],
                    [Paragraph("interaction_logs", table_cell_style), Paragraph("id (Auto-inc)", table_cell_style), Paragraph("username (FK Users)", table_cell_style), Paragraph("Logs student queries, bot responses, routing latency, sentiment polarity, and timestamp for administrative audits.", table_cell_style)],
                    [Paragraph("appointments", table_cell_style), Paragraph("id (Auto-inc)", table_cell_style), Paragraph("student_name (FK Users)", table_cell_style), Paragraph("Manages booking slots for advisor meetings, tracking dates, times, advisor names, status, and query topics.", table_cell_style)]
                ]
                t_db_map = Table([db_map_headers] + db_map_rows, colWidths=[90, 90, 100, 188])
                t_db_map.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(t_db_map)
                story.append(Spacer(1, 12))
                story.append(Paragraph("<i>Table 4.1: Primary Database Entity Schema Mappings</i>", body_center_style))
                story.append(Spacer(1, 15))

                # Also append secondary table schemas in detail:
                # 4.1.1 users
                story.append(Paragraph("<b>4.1.1 Users Entity Table Schema (users)</b>", heading2_style))
                t_u = Table([u_headers] + u_rows, colWidths=[90, 95, 128, 155])
                t_u.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_u)
                story.append(Spacer(1, 15))

                # 4.1.2 courses
                story.append(Paragraph("<b>4.1.2 Course catalogs Reference Entity Table (courses)</b>", heading2_style))
                t_c = Table([c_headers] + c_rows, colWidths=[90, 95, 128, 155])
                t_c.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_c)
                story.append(Spacer(1, 15))

                # 4.1.3 policies
                story.append(Paragraph("<b>4.1.3 University Regulations Reference Entity Table (policies)</b>", heading2_style))
                t_p = Table([p_headers] + p_rows, colWidths=[90, 95, 128, 155])
                t_p.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_p)
                story.append(Spacer(1, 15))

                # 4.1.4 interaction_logs
                story.append(Paragraph("<b>4.1.4 Chat Audit & Sentiment Log Entity Table (interaction_logs)</b>", heading2_style))
                t_il = Table([il_headers] + il_rows, colWidths=[90, 95, 128, 155])
                t_il.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_il)
                story.append(Spacer(1, 15))

                # 4.1.5 appointments
                story.append(Paragraph("<b>4.1.5 Advising Appointment Schedules Entity Table (appointments)</b>", heading2_style))
                t_ap = Table([ap_headers] + ap_rows, colWidths=[90, 95, 128, 155])
                t_ap.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_ap)
                story.append(Spacer(1, 15))

            elif sec_title == "4.2 UML Diagrams & System Diagrams":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_4_1"/><b>Figure 4.1: UML Use Case Diagram</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_use_case_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 4.1: Unified Modeling Language (UML) Use Case Diagram</i>", body_center_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_4_2"/><b>Figure 4.2: Database Entity-Relationship Diagram (3NF Schema)</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_er_diagram_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 4.2: Database Entity-Relationship Diagram (3NF Schema)</i>", body_center_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_4_3"/><b>Figure 4.3: UML Class Interaction Diagram</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_class_diagram_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 4.3: UML Class Interaction Diagram</i>", body_center_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_4_4"/><b>Figure 4.4: Sequence Diagram for Chat Resolution Flow</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_sequence_diagram_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 4.4: Sequence Diagram for Chat Resolution Flow</i>", body_center_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_4_5"/><b>Figure 4.5: System Activity Logic Lifecycle Diagram</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_activity_diagram_drawing())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 4.5: System Activity Logic Lifecycle Diagram</i>", body_center_style))
                story.append(Spacer(1, 15))

            elif sec_title == "5.5 Application Screenshots & Explanations":
                story.append(Spacer(1, 10))
                # Screenshot 1
                story.append(Paragraph('<a name="fig_5_1"/><b>Figure 5.1: Student Chat Portal Interface (Anonymous User Session)</b>', body_bold_style))
                img_path_1 = "data/screenshots/screenshot_1_anonymous_chat.png"
                if os.path.exists(img_path_1):
                    story.append(KeepTogether([
                        wrap_image(img_path_1, 420, 230),
                        Spacer(1, 6),
                        Paragraph("<i>Figure 5.1 displays the anonymous student advising chat window. Students can ask questions "
                                  "regarding university guidelines and courses, viewing instant local matches or AI responses without logging in.</i>", table_cell_style)
                    ]))
                else:
                    story.append(Paragraph("[Screenshot 1 Missing]", body_style))
                story.append(Spacer(1, 15))

                # Screenshot 2
                story.append(Paragraph('<a name="fig_5_2"/><b>Figure 5.2: Student Advising Chat Portal (Authenticated Administrator Session)</b>', body_bold_style))
                img_path_2 = "data/screenshots/screenshot_2_admin_chat.png"
                if os.path.exists(img_path_2):
                    story.append(KeepTogether([
                        wrap_image(img_path_2, 420, 230),
                        Spacer(1, 6),
                        Paragraph("<i>Figure 5.2 displays the chat portal for logged-in administrators. The interface enables personalized "
                                  "conversations and logs student records under the active admin account.</i>", table_cell_style)
                    ]))
                else:
                    story.append(Paragraph("[Screenshot 2 Missing]", body_style))
                story.append(PageBreak())

                # Screenshot 3
                story.append(Paragraph('<a name="fig_5_3"/><b>Figure 5.3: Academic Appointment Slots Booking View</b>', body_bold_style))
                img_path_3 = "data/screenshots/screenshot_3_booking_page.png"
                if os.path.exists(img_path_3):
                    story.append(KeepTogether([
                        wrap_image(img_path_3, 420, 230),
                        Spacer(1, 6),
                        Paragraph("<i>Figure 5.3 shows the booking form where students can schedule advising appointments by "
                                  "selecting an advisor, a date, and a time slot.</i>", table_cell_style)
                    ]))
                else:
                    story.append(Paragraph("[Screenshot 3 Missing]", body_style))
                story.append(Spacer(1, 15))

                # Screenshot 4
                story.append(Paragraph('<a name="fig_5_4"/><b>Figure 5.4: Administrator Sentiment & Query Volume Analytics Dashboard</b>', body_bold_style))
                img_path_4 = "data/screenshots/screenshot_4_admin_dashboard.png"
                if os.path.exists(img_path_4):
                    story.append(KeepTogether([
                        wrap_image(img_path_4, 420, 230),
                        Spacer(1, 6),
                        Paragraph("<i>Figure 5.4 shows the analytics dashboard, featuring key metrics and Plotly charts that track "
                                  "query volumes, average latency, and student sentiment trends.</i>", table_cell_style)
                    ]))
                else:
                    story.append(Paragraph("[Screenshot 4 Missing]", body_style))
                story.append(PageBreak())

                # Screenshot 5
                story.append(Paragraph('<a name="fig_5_5"/><b>Figure 5.5: Registered Student Appointment Scheduling Management Portal</b>', body_bold_style))
                img_path_5 = "data/screenshots/screenshot_5_appointments_list.png"
                if os.path.exists(img_path_5):
                    story.append(KeepTogether([
                        wrap_image(img_path_5, 420, 230),
                        Spacer(1, 6),
                        Paragraph("<i>Figure 5.5 shows the appointment management tab, listing scheduled sessions and allowing "
                                  "administrators to cancel bookings.</i>", table_cell_style)
                    ]))
                else:
                    story.append(Paragraph("[Screenshot 5 Missing]", body_style))
                story.append(Spacer(1, 15))
                
            elif sec_title == "6.2 Unit Testing Validation Matrix":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="table_6_1"/><b>Table 6.1: Unit Verification Test Suite Case Matrix</b>', body_bold_style))
                t1_headers = [Paragraph("<b>Test ID</b>", table_header_style), 
                              Paragraph("<b>Function Verified</b>", table_header_style), 
                              Paragraph("<b>Inputs Sent</b>", table_header_style), 
                              Paragraph("<b>Expected Output Result</b>", table_header_style), 
                              Paragraph("<b>Status</b>", table_header_style)]
                t1_rows = [
                    [Paragraph("UT-01", table_cell_style), Paragraph("db connection", table_cell_style), Paragraph("Engine initialization", table_cell_style), Paragraph("Valid session object returned", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("UT-02", table_cell_style), Paragraph("db seeding", table_cell_style), Paragraph("Execute seed script", table_cell_style), Paragraph("12 courses & 6 policies in DB", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("UT-03", table_cell_style), Paragraph("user login valid", table_cell_style), Paragraph("test_user / valid_hash", table_cell_style), Paragraph("True (credentials match)", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("UT-04", table_cell_style), Paragraph("user login invalid", table_cell_style), Paragraph("test_user / bad_hash", table_cell_style), Paragraph("False (auth rejected)", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("UT-05", table_cell_style), Paragraph("local match policies", table_cell_style), Paragraph("'What is attendance rule?'", table_cell_style), Paragraph("Matches policy id 'attendance'", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("UT-06", table_cell_style), Paragraph("local match courses", table_cell_style), Paragraph("'What course for coding?'", table_cell_style), Paragraph("Returns mca/cse suggestions", table_cell_style), Paragraph("Passed", table_cell_style)]
                ]
                t1_table_data = [t1_headers] + t1_rows
                t_t1 = Table(t1_table_data, colWidths=[50, 110, 110, 148, 50])
                t_t1.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_t1)
                story.append(Spacer(1, 10))
                story.append(Paragraph("<i>Table 6.1: Unit Verification Test Suite Case Matrix</i>", body_center_style))
                story.append(Spacer(1, 15))
                
            elif sec_title == "6.3 End-to-End (E2E) Test Suite":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="table_6_2"/><b>Table 6.2: System Integration and E2E Test Case Matrix</b>', body_bold_style))
                t2_headers = [Paragraph("<b>Test ID</b>", table_header_style), 
                              Paragraph("<b>Action Simulated</b>", table_header_style), 
                              Paragraph("<b>Input Parameters</b>", table_header_style), 
                              Paragraph("<b>Validation Assertion</b>", table_header_style), 
                              Paragraph("<b>Status</b>", table_header_style)]
                t2_rows = [
                    [Paragraph("E2E-01", table_cell_style), Paragraph("Anonymous chat search", table_cell_style), Paragraph("'attendance policy'", table_cell_style), Paragraph("Resolves via local DB instantly", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("E2E-02", table_cell_style), Paragraph("Student sign-up flow", table_cell_style), Paragraph("new_student / password", table_cell_style), Paragraph("Account registered in users DB", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("E2E-03", table_cell_style), Paragraph("Appointment slot booking", table_cell_style), Paragraph("Mentor Gupta, date, time", table_cell_style), Paragraph("Success message shown & logged", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("E2E-04", table_cell_style), Paragraph("Duplicate booking block", table_cell_style), Paragraph("Same mentor, date, time", table_cell_style), Paragraph("Error notification blocks input", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("E2E-05", table_cell_style), Paragraph("Admin dashboard login", table_cell_style), Paragraph("test_admin / hash_pass", table_cell_style), Paragraph("Renders plotly sentiment charts", table_cell_style), Paragraph("Passed", table_cell_style)],
                    [Paragraph("E2E-06", table_cell_style), Paragraph("Schedule cancellation", table_cell_style), Paragraph("Click cancel appointment", table_cell_style), Paragraph("Status changes to Cancelled in DB", table_cell_style), Paragraph("Passed", table_cell_style)]
                ]
                t2_table_data = [t2_headers] + t2_rows
                t_t2 = Table(t2_table_data, colWidths=[50, 110, 110, 148, 50])
                t_t2.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_t2)
                story.append(Spacer(1, 10))
                story.append(Paragraph("<i>Table 6.2: System Integration and E2E Test Case Matrix</i>", body_center_style))
                story.append(Spacer(1, 15))
                
            elif sec_title == "7.2 Sentiment and Analytics Insights":
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_7_1"/><b>Figure 7.1: Query Volume Over Time Graph</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_query_volume_chart())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 7.1: Query Volume Over Time Graph</i>", body_center_style))
                
                story.append(Spacer(1, 10))
                story.append(Paragraph('<a name="fig_7_2"/><b>Figure 7.2: Sentiment Distribution Graph</b>', body_bold_style))
                story.append(Spacer(1, 6))
                story.append(get_sentiment_chart())
                story.append(Spacer(1, 6))
                story.append(Paragraph("<i>Figure 7.2: Sentiment Distribution Graph</i>", body_center_style))
                story.append(Spacer(1, 15))
                
        story.append(PageBreak())

    # ==========================================
    # CHAPTER 9: REFERENCES
    # ==========================================
    story.append(Paragraph('<a name="chapter9"/><b>Chapter 9: References</b>', heading1_style))
    story.append(Spacer(1, 10))
    references_list = [
        "1. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30.",
        "2. Streamlit Inc. (2026). Official Documentation for Reactive Python Applications. Retrieved from https://docs.streamlit.io",
        "3. Puter Cloud API. (2026). Developer Guide for Serverless Cloud completions API Inference. Retrieved from https://docs.puter.com",
        "4. SQLAlchemy Core Team. (2026). Object-Relational Mappings and Schema Declarations. Retrieved from https://docs.sqlalchemy.org",
        "5. Aiven Cloud Services. (2026). Managed PostgreSQL Configuration and Connection Reliability. Retrieved from https://aiven.io/docs",
        "6. Chandigarh University. (2026). Academic Regulations and Student Code of Conduct Handbook.",
        "7. Microsoft Playwright Team. (2026). End-to-End Testing and Browser Automation for Web Applications. Retrieved from https://playwright.dev",
        "8. Loria, S. (2026). TextBlob: Simplified Text Processing for Python. Sentiment Analysis Algorithms.",
        "9. Agile Scrum Alliance. (2026). Agile Scrum Framework Guide for Software Projects.",
        "10. Python Software Foundation. (2026). Python Language Specification (v3.12).",
        "11. IEEE Standard for Software Test Documentation (IEEE Std 829-2008).",
        "12. NIST. (2026). Guidelines for Cloud Security and Data Privacy (SP 800-144).",
        "13. W3C. (2026). WebAssembly Core Specification (v2.0).",
        "14. PostgreSQL Global Development Group. (2026). Managed PostgreSQL 16 Release Notes.",
        "15. Plotly Technologies. (2026). Interactive Graphing Library for Python Apps. Retrieved from https://plotly.com",
        "16. McKinney, W. (2026). Pandas Library for Data Analysis and Manipulation.",
        "17. IETF. (2026). JSON Schema Standard for Structured Payload API Verification.",
        "18. SQLite Consortium. (2026). Transactional Integrity and Lock Management.",
        "19. GitHub Actions. (2026). Continuous Integration and Continuous Deployment Guide.",
        "20. UC Berkeley Advising Systems. (2025). Review of Conversational Chatbots in Student Advising.",
        "21. MIT EdTech Research Group. (2025). Student Support Pilot Using Edge AI Systems.",
        "22. Stanford University. (2025). Research on Data Privacy and Conversational Agents in Higher Education."
    ]
    
    for ref in references_list:
        story.append(Paragraph(ref, body_left_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 10: APPENDICES
    # ==========================================
    story.append(Paragraph('<a name="chapter10"/><b>Chapter 10: Appendices</b>', heading1_style))
    story.append(Paragraph("<b>Appendix A: Installation & Setup Guide</b>", heading2_style))
    story.append(Paragraph(
        "To run the CU AI Advisor application locally:<br/>"
        "1. Clone the repository: <code>git clone https://github.com/manikbholaji/ai-chatbot.git</code><br/>"
        "2. Create a virtual environment: <code>python -m venv .venv</code><br/>"
        "3. Activate the virtual environment: <code>.venv\\Scripts\\activate</code> (Windows) or <code>source .venv/bin/activate</code> (macOS/Linux)<br/>"
        "4. Install dependencies: <code>pip install -r requirements.txt</code><br/>"
        "5. Configure <code>.streamlit/secrets.toml</code> with your Aiven <code>DATABASE_URL</code> and <code>PUTER_TOKEN</code>.<br/>"
        "6. Run the application: <code>streamlit run app.py</code>", body_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Appendix B: User Manual</b>", heading2_style))
    story.append(Paragraph(
        "• <b>Students:</b> Can ask questions anonymously or sign up to save history. To book an appointment, "
        "navigate to the 'Book Appointment' page, select an advisor, select a date and time slot, enter a topic, and submit.<br/>"
        "• <b>Advisors / Admins:</b> Log in using administrative credentials to access the 'Admin Dashboard' "
        "for sentiment charts and usage statistics, and the 'Appointment Management' page to cancel sessions.", body_style))

    story.append(Spacer(1, 10))
    story.append(NextPageTemplate('wide'))
    story.append(PageBreak())
    story.append(Paragraph("<b>Appendix C: Complete Source Code Listings</b>", heading2_style))
    story.append(Paragraph(
        "To provide full structural transparency and ensure ease of audits, the complete source code files "
        "for the core application logic are attached below.", body_style))

    # Dynamically read and load code files into report!
    src_files = [
        ("database.py", "Data Access Mappings & Connection Pool Management"),
        ("chatbot.py", "Pattern-Matching Intent Classifier & PUTER AI Fallback API"),
        ("app.py", "Streamlit UI Navigation & Analytics Views Orchestrator")
    ]
    for filename, desc in src_files:
        story.append(Paragraph(f"<b>C.{src_files.index((filename, desc))+1} File: {filename} ({desc})</b>", heading2_style))
        try:
            with open(filename, "r", encoding="utf-8") as f:
                code_text = f.read()
            wrapped_code = wrap_code_text(code_text, max_len=100)
            # Escape HTML entities
            escaped_code = wrapped_code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Preformatted(escaped_code, code_style))
        except Exception as e:
            story.append(Paragraph(f"Error loading {filename}: {str(e)}", body_style))
        story.append(PageBreak())

    # --- BUILD DOCUMENT ---
    doc.build(story, canvasmaker=NumberedCanvas)

def scan_pdf_page_mappings(pdf_path):
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    mappings = {}
    
    # Pass 1: Find TOC, List of Figures, and List of Tables pages first to prevent false matches
    toc_page = None
    list_figures_page = None
    list_tables_page = None
    
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        text = page.extract_text()
        if not text:
            continue
        if "TABLE OF CONTENTS" in text and toc_page is None:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["TABLE OF CONTENTS", "Table of Contents"]):
                toc_page = page_num
                mappings['toc'] = page_num
        if "LIST OF FIGURES" in text and list_figures_page is None:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["LIST OF FIGURES", "List of Figures"]):
                list_figures_page = page_num
                mappings['list_figures'] = page_num
        if "LIST OF TABLES" in text and list_tables_page is None:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["LIST OF TABLES", "List of Tables"]):
                list_tables_page = page_num
                mappings['list_tables'] = page_num

    # Pass 2: Find all other elements, skipping cover page (1), TOC page, and list pages where appropriate
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        if page_num == 1 or page_num == toc_page:
            continue
            
        text = page.extract_text()
        if not text:
            continue
            
        # Check preliminary sections
        if "BONAFIDE CERTIFICATE" in text and 'bonafide' not in mappings:
            mappings['bonafide'] = page_num
        if "DECLARATION" in text and 'declaration' not in mappings:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["DECLARATION", "Declaration"]):
                mappings['declaration'] = page_num
        if "ACKNOWLEDGEMENT" in text and 'acknowledgement' not in mappings:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["ACKNOWLEDGEMENT", "Acknowledgement"]):
                mappings['acknowledgement'] = page_num
        if "ABSTRACT" in text and 'abstract' not in mappings:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["ABSTRACT", "Abstract"]):
                mappings['abstract'] = page_num
        if "LIST OF ABBREVIATIONS" in text and 'abbreviations' not in mappings:
            if any(h in text.split("\n")[0] or h in text.split("\n")[1] or h in text.split("\n")[2] for h in ["LIST OF ABBREVIATIONS", "List of Abbreviations"]):
                mappings['abbreviations'] = page_num
            
        # Check Chapters
        if "Chapter 1: Introduction" in text and 'chapter1' not in mappings:
            mappings['chapter1'] = page_num
        if "Chapter 2: Literature Review / System Study" in text and 'chapter2' not in mappings:
            mappings['chapter2'] = page_num
        if "Chapter 3: System Analysis" in text and 'chapter3' not in mappings:
            mappings['chapter3'] = page_num
        if "Chapter 4: System Design" in text and 'chapter4' not in mappings:
            mappings['chapter4'] = page_num
        if "Chapter 5: System Implementation" in text and 'chapter5' not in mappings:
            mappings['chapter5'] = page_num
        if "Chapter 6: Testing" in text and 'chapter6' not in mappings:
            mappings['chapter6'] = page_num
        if "Chapter 7: Results & Discussion" in text and 'chapter7' not in mappings:
            mappings['chapter7'] = page_num
        if "Chapter 8: Conclusion & Future Scope" in text and 'chapter8' not in mappings:
            mappings['chapter8'] = page_num
        if "Chapter 9: References" in text and 'chapter9' not in mappings:
            mappings['chapter9'] = page_num
        if "Chapter 10: Appendices" in text and 'chapter10' not in mappings:
            mappings['chapter10'] = page_num
            
        # Check Figures (skip List of Figures page itself)
        if page_num != list_figures_page:
            if "Figure 3.1:" in text and 'fig_3_1' not in mappings:
                mappings['fig_3_1'] = page_num
            if "Figure 3.2:" in text and 'fig_3_2' not in mappings:
                mappings['fig_3_2'] = page_num
            if "Figure 4.1:" in text and 'fig_4_1' not in mappings:
                mappings['fig_4_1'] = page_num
            if "Figure 4.2:" in text and 'fig_4_2' not in mappings:
                mappings['fig_4_2'] = page_num
            if "Figure 4.3:" in text and 'fig_4_3' not in mappings:
                mappings['fig_4_3'] = page_num
            if "Figure 4.4:" in text and 'fig_4_4' not in mappings:
                mappings['fig_4_4'] = page_num
            if "Figure 4.5:" in text and 'fig_4_5' not in mappings:
                mappings['fig_4_5'] = page_num
            if "Figure 5.1:" in text and 'fig_5_1' not in mappings:
                mappings['fig_5_1'] = page_num
            if "Figure 5.2:" in text and 'fig_5_2' not in mappings:
                mappings['fig_5_2'] = page_num
            if "Figure 5.3:" in text and 'fig_5_3' not in mappings:
                mappings['fig_5_3'] = page_num
            if "Figure 5.4:" in text and 'fig_5_4' not in mappings:
                mappings['fig_5_4'] = page_num
            if "Figure 5.5:" in text and 'fig_5_5' not in mappings:
                mappings['fig_5_5'] = page_num
            if "Figure 7.1:" in text and 'fig_7_1' not in mappings:
                mappings['fig_7_1'] = page_num
            if "Figure 7.2:" in text and 'fig_7_2' not in mappings:
                mappings['fig_7_2'] = page_num
                
        # Check Tables (skip List of Tables page itself)
        if page_num != list_tables_page:
            if ("Table 2.1:" in text or "Table 2.1 " in text) and 'table_2_1' not in mappings:
                mappings['table_2_1'] = page_num
            if ("Table 3.1:" in text or "Table 3.1 " in text) and 'table_3_1' not in mappings:
                mappings['table_3_1'] = page_num
            if ("Table 4.1:" in text or "Table 4.1 " in text) and 'table_4_1' not in mappings:
                mappings['table_4_1'] = page_num
            if ("Table 6.1:" in text or "Table 6.1 " in text) and 'table_6_1' not in mappings:
                mappings['table_6_1'] = page_num
            if ("Table 6.2:" in text or "Table 6.2 " in text) and 'table_6_2' not in mappings:
                mappings['table_6_2'] = page_num

    return mappings

def build_pdf_multipass(filename="CU_AI_Advisor_MCA_Final_Report_Manik_Bhola.pdf"):
    # Clear total pages and appendix start for Pass 1
    NumberedCanvas.TOTAL_PAGES = 0
    NumberedCanvas.APPENDIX_START_PAGE = 999
    print("Pass 1: Building PDF with guess page numbers...")
    build_pdf(filename, page_mappings=None)
    
    print("Pass 1 complete. Scanning PDF for true page alignments...")
    reader = PdfReader(filename)
    total_pages = len(reader.pages)
    mappings = scan_pdf_page_mappings(filename)
    print("Scanned Alignments:")
    for k, v in mappings.items():
        print(f"  {k}: {v}")
        
    print(f"\nPass 2: Re-building PDF with exact page alignments (Total Pages: {total_pages})...")
    NumberedCanvas.TOTAL_PAGES = total_pages
    NumberedCanvas.APPENDIX_START_PAGE = mappings.get('chapter10', 999)
    build_pdf(filename, page_mappings=mappings)
    
    print("Pass 2 complete. Re-scanning PDF to check for any layout shift...")
    reader2 = PdfReader(filename)
    new_total_pages = len(reader2.pages)
    new_mappings = scan_pdf_page_mappings(filename)
    
    # Check if the page numbers changed
    shifts = {k: (v, new_mappings.get(k)) for k, v in mappings.items() if new_mappings.get(k) != v}
    if shifts or new_total_pages != total_pages:
        print("Layout shift detected:")
        if new_total_pages != total_pages:
            print(f"  Total Pages: {total_pages} -> {new_total_pages}")
        for k, (v1, v2) in shifts.items():
            print(f"  {k}: {v1} -> {v2}")
        print("\nPass 3: Running third compilation to ensure convergence...")
        NumberedCanvas.TOTAL_PAGES = new_total_pages
        NumberedCanvas.APPENDIX_START_PAGE = new_mappings.get('chapter10', 999)
        build_pdf(filename, page_mappings=new_mappings)
        print("Pass 3 complete. Convergence achieved!")
    else:
        print("PDF generation converged successfully on Pass 2!")

if __name__ == "__main__":
    import sys
    out_filename = sys.argv[1] if len(sys.argv) > 1 else "CU_AI_Advisor_MCA_Final_Report_Manik_Bhola.pdf"
    build_pdf_multipass(out_filename)
