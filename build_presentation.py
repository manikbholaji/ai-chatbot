from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Frame, PageTemplate, NextPageTemplate
)
from reportlab.graphics.shapes import Drawing, Group
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas

# Import vector diagrams from drawings.py
from drawings import (
    get_dfd_level_0_drawing,
    get_dfd_level_1_drawing,
    get_use_case_drawing,
    get_class_diagram_drawing,
    get_sequence_diagram_drawing,
    get_activity_diagram_drawing,
    get_query_volume_chart,
    get_sentiment_chart
)

# Colors
COLOR_NAVY = colors.HexColor("#1A365D")
COLOR_SLATE = colors.HexColor("#475569")
COLOR_BORDER = colors.HexColor("#CBD5E1")
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")
COLOR_TEXT_DARK = colors.HexColor("#1A202C")
COLOR_GOLD = colors.HexColor("#D69E2E")

# Scale drawing helper to fit within slide columns
def scale_drawing(d, target_width):
    scale_factor = target_width / d.width
    d_scaled = Drawing(target_width, d.height * scale_factor)
    g = Group()
    g.scale(scale_factor, scale_factor)
    for child in d.contents:
        g.add(child)
    d_scaled.add(g)
    return d_scaled

def draw_cover_background(canvas, doc):
    canvas.saveState()
    # Draw dark navy background
    canvas.setFillColor(COLOR_NAVY)
    canvas.rect(0, 0, 792, 612, fill=True, stroke=False)
    
    # Gold borders
    canvas.setStrokeColor(COLOR_GOLD)
    canvas.setLineWidth(2)
    canvas.rect(20, 20, 752, 572)
    canvas.setLineWidth(0.5)
    canvas.rect(24, 24, 744, 564)
    canvas.restoreState()

def draw_content_background(canvas, doc):
    canvas.saveState()
    # Draw light background card
    canvas.setFillColor(COLOR_BG_LIGHT)
    canvas.rect(0, 0, 792, 612, fill=True, stroke=False)
    
    # Draw slide borders
    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(0.5)
    canvas.rect(15, 15, 762, 582)
    
    # Top header bar
    canvas.setFillColor(COLOR_NAVY)
    canvas.rect(15, 545, 762, 52, fill=True, stroke=False)
    
    # Header line separator
    canvas.setStrokeColor(COLOR_GOLD)
    canvas.setLineWidth(1.5)
    canvas.line(15, 545, 777, 545)
    
    # Running Footer line separator
    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(15, 45, 777, 45)
    canvas.restoreState()

class PresentationCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        # Slide 1 & Last Slide (14) are cover pages - no footer
        if self._pageNumber != 1 and self._pageNumber != total_pages:
            # Footer Left Text
            self.setFont("Times-Bold", 8)
            self.setFillColor(COLOR_SLATE)
            self.drawString(25, 30, "CU AI Advisor | Department of Computer Applications")
            
            # Footer Center Text
            self.drawCentredString(396, 30, f"Slide {self._pageNumber} of {total_pages}")
            
            # Footer Right Text
            self.drawRightString(767, 30, "Manik Bhola | O24MCA110817")
            
        self.restoreState()

# Using reportlab.platypus.NextPageTemplate instead of custom switcher

def build_pdf(filename="CU_AI_Advisor_MCA_Project_Presentation.pdf"):
    # Landscape Letter: 792 x 612 points
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=35,
        rightMargin=35,
        topMargin=35,
        bottomMargin=35
    )
    
    # Frames
    cover_frame = Frame(35, 35, 722, 542, id='cover_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    content_frame = Frame(35, 55, 722, 535, id='content_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    
    cover_template = PageTemplate(id='First', frames=[cover_frame], onPage=draw_cover_background)
    content_template = PageTemplate(id='Later', frames=[content_frame], onPage=draw_content_background)
    
    doc.pageTemplates = []
    doc.addPageTemplates([cover_template, content_template])
    
    # Custom Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Times-Bold',
        fontSize=32,
        leading=38,
        alignment=TA_CENTER,
        textColor=colors.white,
        spaceAfter=15
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        fontName='Times-Roman',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=COLOR_BORDER,
        spaceAfter=30
    )
    
    style_cover_label = ParagraphStyle(
        'CoverLabel',
        fontName='Times-Bold',
        fontSize=14,
        leading=17,
        textColor=COLOR_GOLD,
        spaceAfter=5
    )
    
    style_cover_val = ParagraphStyle(
        'CoverValue',
        fontName='Times-Roman',
        fontSize=13,
        leading=16,
        textColor=colors.white,
        spaceAfter=15
    )
    
    style_cover_date = ParagraphStyle(
        'CoverDate',
        fontName='Times-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=COLOR_GOLD,
        spaceBefore=25
    )
    
    style_slide_title = ParagraphStyle(
        'SlideTitle',
        fontName='Times-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.white,
        spaceAfter=15
    )
    
    style_bullet = ParagraphStyle(
        'SlideBullet',
        fontName='Times-Roman',
        fontSize=16,
        leading=22,
        textColor=COLOR_TEXT_DARK,
        leftIndent=15,
        firstLineIndent=-12,
        spaceAfter=12
    )
    
    style_caption = ParagraphStyle(
        'SlideCaption',
        fontName='Times-Italic',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=COLOR_SLATE,
        spaceBefore=10
    )
    
    story = []
    
    # ----------------------------------------------------
    # SLIDE 1: Cover Slide
    # ----------------------------------------------------
    # Starts on template 'First' automatically
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>CHANDIGARH UNIVERSITY</b>", style_cover_subtitle))
    story.append(Paragraph("<b>CU AI ADVISOR: A CLOUD-NATIVE SERVERLESS ACADEMIC ADVISING SYSTEM</b>", style_cover_title))
    story.append(Paragraph(
        "Project Presentation submitted in partial fulfillment of the requirements for the award of the degree of<br/>"
        "<b>Master of Computer Applications (MCA)</b>", style_cover_subtitle))
    
    story.append(Spacer(1, 25))
    
    # Two-column layout for details
    left_details = [
        Paragraph("<b>Submitted By:</b>", style_cover_label),
        Paragraph("<b>Name:</b> Manik Bhola", style_cover_val),
        Paragraph("<b>Roll Number:</b> O24MCA110817", style_cover_val),
        Paragraph("<b>Batch:</b> 2024-2026", style_cover_val)
    ]
    
    right_details = [
        Paragraph("<b>Under the Guidance of:</b>", style_cover_label),
        Paragraph("<b>Guide:</b> Kashish Gupta", style_cover_val),
        Paragraph("<b>Designation:</b> Assistant Professor & Mentor", style_cover_val),
        Paragraph("<b>Department:</b> Computer Applications", style_cover_val)
    ]
    
    det_table = Table([[left_details, right_details]], colWidths=[350, 350])
    det_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(det_table)
    
    story.append(Paragraph("<b>Submission Date & Place: June 2026, Ludhiana</b>", style_cover_date))
    story.append(NextPageTemplate('Later'))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # Set to Content Page Template
    # ----------------------------------------------------
    
    def make_bullet_slide(title, bullets):
        # Generates a standard content slide flowable
        slide_flowables = [
            Paragraph(title, style_slide_title),
            Spacer(1, 35)
        ]
        bullet_flowables = []
        for b in bullets:
            bullet_flowables.append(Paragraph(b, style_bullet))
        slide_flowables.extend(bullet_flowables)
        return slide_flowables

    def make_split_slide(title, bullets, visual_flowable, visual_width=350, caption=""):
        # 2-Column slide flowable: text left, drawing/chart/table right
        left_flow = []
        for b in bullets:
            left_flow.append(Paragraph(b, style_bullet))
            
        if isinstance(visual_flowable, list):
            right_flow = list(visual_flowable)
        else:
            right_flow = [visual_flowable]
            
        if caption:
            right_flow.append(Paragraph(caption, style_caption))
            
        t = Table([[left_flow, right_flow]], colWidths=[310, 390])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        return [
            Paragraph(title, style_slide_title),
            Spacer(1, 35),
            t
        ]

    # ----------------------------------------------------
    # SLIDE 2: Abstract
    # ----------------------------------------------------
    story.extend(make_bullet_slide(
        "Abstract / Executive Summary",
        [
            "• <b>Topic of Study:</b> An intelligent, cloud-native conversational agent designed to provide 24/7 academic advising, course suggestions, and policy lookups for Chandigarh University students.",
            "• <b>System Objective:</b> Automate catalog search and advising schedules to offload the manual student support pipeline.",
            "• <b>Methodology:</b> Agile Scrum framework featuring reactive Streamlit UI orchestration and client-side serverless completions.",
            "• <b>Key Findings:</b> Successfully decoupled database writes and heavy inference, reducing cloud server hosting costs to zero by executing AI prompting natively on client-side sandboxes.",
            "• <b>Conclusion:</b> A highly scalable, fault-tolerant advising chatbot capable of maintaining transactional integrity (SQLite/PostgreSQL) and database compliance."
        ]
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 3: Introduction
    # ----------------------------------------------------
    story.extend(make_bullet_slide(
        "Introduction & System Background",
        [
            "• <b>Context:</b> Scalable academic advising is an operational bottleneck in modern large-scale higher education institutions.",
            "• <b>Problem Statement:</b> Traditional manual advisor slot booking and catalog browsing lead to delayed sessions and inconsistent advice.",
            "• <b>Proposed System:</b> The CU AI Advisor leverages Streamlit and the serverless Puter completions API to serve queries instantly.",
            "• <b>Hybrid Routing:</b> Integrates local keyword and regex intent classifiers with generative fallback loops to maintain strict guardrails.",
            "• <b>Security & Speed:</b> Direct client-side AI integration bypasses institutional database locks, maintaining 100% data security."
        ]
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 4: Literature Review & Gap Analysis
    # ----------------------------------------------------
    story.extend(make_bullet_slide(
        "Literature Review & Theoretical Framework",
        [
            "• <b>Similar Systems:</b> Traditional advising bots depend on heavy server-side hosting (e.g. AWS EC2/ECS) or costly commercial APIs.",
            "• <b>Research Gap:</b> Lack of decentralized, serverless execution architectures for database-integrated university chatbots.",
            "• <b>Waterfall vs. Agile:</b> Adopted Agile Scrum iterative development cycle (June 1 - June 13) to facilitate rapid sprint testing.",
            "• <b>Framework Selection:</b> Streamlit chosen for immediate frontend-backend reactive binding; SQLAlchemy selected for absolute database porting.",
            "• <b>Novel Architecture:</b> Implements local rule-matching fallback to resolve common queries without generating LLM token charges."
        ]
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 5: System Analysis - DFD 0
    # ----------------------------------------------------
    dfd0 = scale_drawing(get_dfd_level_0_drawing(), 350)
    story.extend(make_split_slide(
        "System Analysis: DFD Level 0 Context Diagram",
        [
            "• <b>Feasibility Study:</b> Evaluated operational and technical feasibility; confirmed 100% compatibility with local and cloud setups.",
            "• <b>Process 0.0:</b> Represents the central advisor system portal coordinating all database and API components.",
            "• <b>External Entities:</b> Student User (queries/bookings), Admin User (logs/dashboard), and the external Puter AI completions API.",
            "• <b>Data Boundaries:</b> Shows data boundaries where local rules are analyzed prior to invoking external API services."
        ],
        dfd0,
        caption="Figure 5.1: Context Level Data Flow Diagram"
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 6: System Analysis - DFD 1
    # ----------------------------------------------------
    dfd1 = scale_drawing(get_dfd_level_1_drawing(), 350)
    story.extend(make_split_slide(
        "System Analysis: DFD Level 1 Process Flow",
        [
            "• <b>Modularization:</b> Process 0.0 is broken down into Auth (1.0), Chat (2.0), Edge AI (3.0), Booking (4.0), and Analytics (5.0).",
            "• <b>Security Boundary:</b> Auth separates Student roles from Admin dashboard privileges.",
            "• <b>Intent Dispatching:</b> Chat Router evaluates input and redirects to Edge AI if no local match is found.",
            "• <b>Data Persistence:</b> Visualizes write operations to appointments database and read queries for analytics graphs."
        ],
        dfd1,
        caption="Figure 6.1: Detailed Process Level Data Flow Diagram"
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 7: System Design - Use Case & Class Diagram
    # ----------------------------------------------------
    uc_drawing = scale_drawing(get_use_case_drawing(), 350)
    class_drawing = scale_drawing(get_class_diagram_drawing(), 350)
    
    story.extend(make_split_slide(
        "System Design: UML Use Case & Class Diagram",
        [
            "• <b>Actor Roles:</b> Use Case diagram defines Students (querying, booking) and Admins (dashboard management).",
            "• <b>Entity Models:</b> Class diagram displays structured models for `DatabaseManager` and `ChatController`.",
            "• <b>Object Relationships:</b> Enforces dependency injection where `ChatController` uses `DatabaseManager` for session transactions.",
            "• <b>Multi-Compartment Mappings:</b> Outlines attributes and operational methods in complete UML format."
        ],
        [uc_drawing, Spacer(1, 10), class_drawing],
        caption="Figure 7.1: UML Use Case (top) and Class Diagram (bottom)"
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 8: System Design - Sequence & Activity Diagram
    # ----------------------------------------------------
    seq_drawing = scale_drawing(get_sequence_diagram_drawing(), 350)
    act_drawing = scale_drawing(get_activity_diagram_drawing(), 350)
    
    story.extend(make_split_slide(
        "System Design: Sequence & Activity Diagram",
        [
            "• <b>Message Sequencing:</b> Sequence diagram displays step-by-step lifelines from Student to DB and Puter AI.",
            "• <b>Execution Control:</b> Employs strict UML activation blocks matching message send/receive timings.",
            "• <b>Decision Lifecycles:</b> Activity diagram maps the routing logic for matching local catalogs before fallback.",
            "• <b>Bypass Routing:</b> Employs non-overlapping bypass lines to map output merging into the Logging database."
        ],
        [seq_drawing, Spacer(1, 10), act_drawing],
        caption="Figure 8.1: UML Sequence Flow (top) and Activity Decisions (bottom)"
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 9: System Implementation
    # ----------------------------------------------------
    story.extend(make_bullet_slide(
        "System Implementation Details",
        [
            "• <b>Tech Stack:</b> Implemented in Python 3.14 utilizing reactive Streamlit UI templates.",
            "• <b>Reliable Connection Pool:</b> Built SQLAlchemy database layer with Aiven PostgreSQL integration and automatic `sslmode=require` query parameters.",
            "• <b>Upsert-Based Seeding:</b> Upsert queries populate and synchronize 12 course configurations (including B.Des Fashion Design) without data duplication.",
            "• <b>Outage Resilience:</b> Configured UI fallbacks that show helpful advising templates if Puter AI connection drops.",
            "• <b>Security:</b> Direct database isolation ensures user passwords are encrypted using SHA-256."
        ]
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 10: Testing & Verification
    # ----------------------------------------------------
    # Create test case table
    test_data = [
        ["Test ID", "Input", "Expected Output", "Actual Output", "Status"],
        ["TC-01", "Invalid Login", "Display error", "Invalid credentials", "PASS"],
        ["TC-02", "Book Slot", "Save record", "Slot booked in DB", "PASS"],
        ["TC-03", "Ask Course", "Regex Match", "Display course info", "PASS"],
        ["TC-04", "Puter AI Drop", "Fallback template", "Assistant card shown", "PASS"]
    ]
    test_table = Table(test_data, colWidths=[55, 80, 100, 100, 50])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    story.extend(make_split_slide(
        "Testing & Quality Assurance Metrics",
        [
            "• <b>Test Coverage:</b> Programmed 23 automated unit and end-to-end browser tests using pytest and Playwright.",
            "• <b>E2E Browser Validation:</b> Automated Playwright scripts simulate authentication, chat queries, and dashboard metrics.",
            "• <b>Database Mocking:</b> Utilizes SQLite mock databases to isolate and verify SQL transactions.",
            "• <b>Test Results:</b> 100% test success rate (23/23 passing) across all database connection and seeding suites."
        ],
        test_table,
        caption="Table 10.1: Core System Test Scenarios"
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 11: Data Analysis & Results
    # ----------------------------------------------------
    volume_chart = scale_drawing(get_query_volume_chart(), 350)
    sentiment_chart = scale_drawing(get_sentiment_chart(), 350)
    
    story.extend(make_split_slide(
        "Results: Query Analytics & Sentiment Breakdown",
        [
            "• <b>Daily Query Volume:</b> Real-time dashboard plots daily query metrics from June 1 (12) to June 13 (58).",
            "• <b>Sentiment Classification:</b> Evaluates customer feedback; successfully logs 60% Positive, 25% Neutral, and 15% Negative scores.",
            "• <b>Dashboard Integration:</b> Admin analytics display Plotly line charts and breakdowns dynamically.",
            "• <b>Operational Impact:</b> Demonstrates system scalability and capability to support university enrollment volumes."
        ],
        [volume_chart, Spacer(1, 10), sentiment_chart],
        caption="Figure 11.1: Query Volume Line Graph (top) and Sentiment Distribution (bottom)"
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 12: Conclusions & Future Scope
    # ----------------------------------------------------
    story.extend(make_bullet_slide(
        "Conclusions & Future Scope",
        [
            "• <b>Objectives Met:</b> Developed a 24/7 academic advisor that handles appointment scheduling and course lookups.",
            "• <b>Infrastructure Savings:</b> Reduced operational hosting costs to zero by using client-side Puter AI completions.",
            "• <b>Technical Growth:</b> Built deep expertise in serverless architectures, 3NF schema design, and E2E browser testing.",
            "• <b>Cloud Expansion:</b> Future versions will port logging logic to AWS Lambda and configure auto-scaling PostgreSQL.",
            "• <b>Feature Upgrades:</b> Plan to add native Google Calendar sync and integrated role-based payment portals."
        ]
    ))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 13: Project Limitations
    # ----------------------------------------------------
    story.extend(make_bullet_slide(
        "Project Limitations",
        [
            "• <b>Token Limits:</b> Puter AI completions API enforces standard limits, which may restrict high-throughput student sessions.",
            "• <b>Connectivity Dependencies:</b> Client-side AI execution requires student devices to have active internet connections.",
            "• <b>Data Persistence:</b> Hybrid fallbacks cannot sync interaction logs to Aiven DB when offline.",
            "• <b>Local Context Size:</b> Regex pattern dictionary requires ongoing administrative updates as academic catalogs evolve.",
            "• <b>Browser Sandbox:</b> Client-side executions are constrained by local browser performance and storage limits."
        ]
    ))
    story.append(NextPageTemplate('First'))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SLIDE 14: Thank You (Cover Template)
    # ----------------------------------------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("<b>THANK YOU</b>", style_cover_title))
    story.append(Paragraph("<b>Questions & Answers</b>", style_cover_subtitle))
    
    story.append(Spacer(1, 40))
    
    presenter_details = [
        Paragraph("<b>Presenter:</b> Manik Bhola", style_cover_val),
        Paragraph("<b>Roll Number:</b> O24MCA110817", style_cover_val),
        Paragraph("<b>Degree:</b> MCA (Batch: 2024-2026)", style_cover_val),
        Paragraph("<b>Guide:</b> Kashish Gupta (Assistant Professor)", style_cover_val),
        Paragraph("<b>Institution:</b> Chandigarh University", style_cover_val)
    ]
    
    pres_table = Table([[presenter_details]], colWidths=[400])
    pres_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(pres_table)
    
    doc.build(story, canvasmaker=PresentationCanvas)

if __name__ == "__main__":
    build_pdf()
