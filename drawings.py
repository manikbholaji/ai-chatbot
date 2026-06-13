# -*- coding: utf-8 -*-
# High-quality vector graphics drawings for CU AI Advisor report
# Using ReportLab native Drawing and Shape flowables for professional visual evaluation

from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Line, Polygon, Group, Ellipse
from reportlab.lib import colors

# --- COLOR PALETTE DEFINITIONS ---
COLOR_NAVY = colors.HexColor("#1A365D")
COLOR_SLATE = colors.HexColor("#475569")
COLOR_BORDER = colors.HexColor("#CBD5E1")
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")
COLOR_GREEN = colors.HexColor("#34A853")
COLOR_YELLOW = colors.HexColor("#FBBC05")
COLOR_RED = colors.HexColor("#EA4335")
COLOR_TEXT_DARK = colors.HexColor("#1A202C")
COLOR_TEXT_LIGHT = colors.white

def draw_arrow(g, x1, y1, x2, y2, label="", label_pos="top"):
    """Draws a line with an arrowhead from (x1, y1) to (x2, y2)."""
    # Main line
    g.add(Line(x1, y1, x2, y2, strokeColor=COLOR_SLATE, strokeWidth=1))
    
    # Calculate arrowhead direction
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Arrowhead length and spread
    arrow_len = 6
    arrow_angle = math.pi / 6  # 30 degrees
    
    xa = x2 - arrow_len * math.cos(angle - arrow_angle)
    ya = y2 - arrow_len * math.sin(angle - arrow_angle)
    xb = x2 - arrow_len * math.cos(angle + arrow_angle)
    yb = y2 - arrow_len * math.sin(angle + arrow_angle)
    
    g.add(Polygon([x2, y2, xa, ya, xb, yb], fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    
    # Draw label if provided
    if label:
        lx = (x1 + x2) / 2
        ly = (y1 + y2) / 2
        if label_pos == "top":
            ly += 5
        elif label_pos == "bottom":
            ly -= 10
        elif label_pos == "left":
            lx -= len(label)*3 - 5
        elif label_pos == "right":
            lx += len(label)*3 - 5
        g.add(String(lx, ly, label, fontName="Helvetica", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))

def draw_stick_figure(g, x, y, label=""):
    """Draws a stick figure actor at (x, y)."""
    # Head
    g.add(Circle(x, y + 25, 6, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_NAVY, strokeWidth=1.5))
    # Body
    g.add(Line(x, y + 19, x, y + 5, strokeColor=COLOR_NAVY, strokeWidth=1.5))
    # Arms
    g.add(Line(x - 10, y + 14, x + 10, y + 14, strokeColor=COLOR_NAVY, strokeWidth=1.5))
    # Legs
    g.add(Line(x, y + 5, x - 8, y - 5, strokeColor=COLOR_NAVY, strokeWidth=1.5))
    g.add(Line(x, y + 5, x + 8, y - 5, strokeColor=COLOR_NAVY, strokeWidth=1.5))
    
    # Label
    if label:
        g.add(String(x, y - 15, label, fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_NAVY, textAnchor="middle"))

def add_header_footer_to_drawing(d, width, height, title):
    """Draws a background card container around the diagram."""
    # Light gray card background
    d.add(Rect(0, 0, width, height, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_BORDER, strokeWidth=0.5, rx=6, ry=6))
    # Outer margin border
    d.add(Rect(2, 2, width-4, height-4, fillColor=None, strokeColor=COLOR_BORDER, strokeWidth=0.5, rx=4, ry=4))

# ==========================================
# 1. Figure 3.1: DFD Level 0 Context Diagram
# ==========================================
def get_dfd_level_0_drawing():
    w, h = 468, 220
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "DFD Level 0 Context Diagram")
    
    g = Group()
    # Left Actor: Student User
    g.add(Rect(20, 95, 90, 40, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=3, ry=3))
    g.add(String(65, 117, "STUDENT", fontName="Helvetica-Bold", fontSize=9, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(65, 105, "USER", fontName="Helvetica-Bold", fontSize=9, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Right Actor: Admin User
    g.add(Rect(358, 95, 90, 40, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=3, ry=3))
    g.add(String(403, 117, "ADMIN", fontName="Helvetica-Bold", fontSize=9, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(403, 105, "USER", fontName="Helvetica-Bold", fontSize=9, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Center Process: System Portal
    g.add(Circle(234, 115, 45, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    g.add(String(234, 125, "CU AI ADVISOR", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(234, 115, "SYSTEM PORTAL", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(234, 105, "(Process 0.0)", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Bottom: External Puter AI Edge API
    g.add(Rect(154, 10, 160, 25, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_BORDER, rx=2, ry=2))
    g.add(String(234, 21, "Puter AI Platform API (Edge AI)", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_NAVY, textAnchor="middle"))
    g.add(String(234, 13, "External Client-Side Endpoint", fontName="Helvetica", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # Data flow arrows
    # Student -> Center (Queries)
    draw_arrow(g, 110, 125, 189, 125, "Queries", "top")
    # Center -> Student (Advice / Bookings)
    draw_arrow(g, 189, 105, 110, 105, "Advice/Slots", "bottom")
    
    # Admin -> Center (Credentials / Configuration)
    draw_arrow(g, 358, 125, 279, 125, "Credentials/Actions", "top")
    # Center -> Admin (Dashboard data)
    draw_arrow(g, 279, 105, 358, 105, "Analytics/Logs", "bottom")
    
    # Center -> Puter AI
    draw_arrow(g, 220, 70, 220, 35, "Prompt API", "left")
    # Puter AI -> Center
    draw_arrow(g, 248, 35, 248, 70, "Response tokens", "right")
    
    d.add(g)
    return d

# ==========================================
# 2. Figure 3.2: DFD Level 1 System Data Flow Diagram
# ==========================================
def get_dfd_level_1_drawing():
    w, h = 468, 225
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "DFD Level 1 System Data Flow Diagram")
    
    g = Group()
    # Entities
    # Left: Student
    g.add(Rect(10, 140, 60, 30, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=2, ry=2))
    g.add(String(40, 152, "STUDENT", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Right: Admin
    g.add(Rect(398, 140, 60, 30, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=2, ry=2))
    g.add(String(428, 152, "ADMIN", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Processes (Circles, r=20)
    # Process 1: Login
    g.add(Circle(120, 155, 20, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    g.add(String(120, 158, "1.0", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(120, 148, "Login/Reg", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Process 2: Chat
    g.add(Circle(120, 85, 20, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    g.add(String(120, 88, "2.0", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(120, 78, "Chat Router", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Process 3: Edge AI
    g.add(Circle(240, 85, 20, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    g.add(String(240, 88, "3.0", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(240, 78, "Edge AI", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Process 4: Booking
    g.add(Circle(240, 155, 20, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    g.add(String(240, 158, "4.0", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(240, 148, "Book Appt", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Process 5: Analytics
    g.add(Circle(340, 155, 20, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE))
    g.add(String(340, 158, "5.0", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    g.add(String(340, 148, "Analytics", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
    
    # Data Stores (Horizontal bars top/bottom, open on right)
    # D1: Users Table
    g.add(Line(10, 210, 80, 210, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(Line(10, 195, 80, 195, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(String(45, 200, "D1: users", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # D2/D3: Catalogs / Policies
    g.add(Line(180, 40, 300, 40, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(Line(180, 25, 300, 25, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(String(240, 30, "D2/D3: courses / policies", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # D4: Appointments Table
    g.add(Line(200, 210, 280, 210, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(Line(200, 195, 280, 195, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(String(240, 200, "D4: appointments", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # D5: Interaction Logs Table
    g.add(Line(320, 210, 400, 210, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(Line(320, 195, 400, 195, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(String(360, 200, "D5: interaction_logs", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # Data Flows (Arrows)
    # Student -> 1.0 Login
    draw_arrow(g, 70, 160, 100, 160, "Creds", "top")
    # 1.0 -> D1
    draw_arrow(g, 106, 169, 60, 195)
    # Student -> 2.0 Chat
    draw_arrow(g, 40, 140, 102, 95, "Query", "left")
    # 2.0 -> D2/D3 (Local Match Query)
    draw_arrow(g, 135, 70, 190, 40)
    # 2.0 -> 3.0 (Fallback)
    draw_arrow(g, 140, 85, 220, 85, "No Match", "top")
    # 3.0 -> 2.0 (Response)
    draw_arrow(g, 220, 80, 140, 80, "Response", "bottom")
    # Student -> 4.0 Booking
    draw_arrow(g, 50, 140, 220, 145, "Book", "bottom")
    # 4.0 -> D4
    draw_arrow(g, 240, 175, 240, 195, "Write", "left")
    # Admin -> 5.0 Analytics
    draw_arrow(g, 398, 155, 360, 155, "Views", "bottom")
    # 5.0 -> D5 (Reads logs)
    draw_arrow(g, 350, 175, 355, 195)
    
    # Return flows (simple lines without heavy arrows to keep clean)
    g.add(Line(100, 85, 70, 140, strokeColor=COLOR_SLATE, strokeWidth=0.5))
    g.add(Line(220, 155, 70, 140, strokeColor=COLOR_SLATE, strokeWidth=0.5))
    
    d.add(g)
    return d

# ==========================================
# 3. Figure 4.1: UML Use Case Diagram
# ==========================================
def get_use_case_drawing():
    w, h = 468, 200
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "UML Use Case Diagram")
    
    g = Group()
    # System boundary box
    g.add(Rect(90, 15, 288, 170, fillColor=colors.white, strokeColor=COLOR_SLATE, strokeWidth=1, rx=4, ry=4))
    g.add(String(234, 170, "CU AI Advisor System", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # Draw Actors
    draw_stick_figure(g, 45, 85, "Student")
    draw_stick_figure(g, 423, 85, "Administrator")
    
    # Draw Use Case Ellipses
    # UC1: Ask Advice
    g.add(Ellipse(234, 140, 65, 12, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_NAVY))
    g.add(String(234, 137, "Ask Academic Advice", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK, textAnchor="middle"))
    
    # UC2: Search Catalog
    g.add(Ellipse(234, 110, 65, 12, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_NAVY))
    g.add(String(234, 107, "Search Courses & Rules", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK, textAnchor="middle"))
    
    # UC3: Book Appointment
    g.add(Ellipse(234, 80, 65, 12, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_NAVY))
    g.add(String(234, 77, "Book Advising Slot", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK, textAnchor="middle"))
    
    # UC4: Manage Appointments
    g.add(Ellipse(234, 50, 65, 12, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_NAVY))
    g.add(String(234, 47, "Manage Schedules", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK, textAnchor="middle"))
    
    # UC5: View Analytics
    g.add(Ellipse(234, 25, 65, 12, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_NAVY))
    g.add(String(234, 22, "View Dashboard", fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK, textAnchor="middle"))
    
    # Association Lines
    # Student associations
    g.add(Line(65, 110, 169, 140, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    g.add(Line(65, 105, 169, 110, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    g.add(Line(65, 100, 169, 80, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    
    # Admin associations
    g.add(Line(403, 110, 299, 110, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    g.add(Line(403, 105, 299, 80, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    g.add(Line(403, 100, 299, 50, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    g.add(Line(403, 95, 299, 25, strokeColor=COLOR_SLATE, strokeWidth=0.8))
    
    d.add(g)
    return d

# ==========================================
# 4. Figure 4.2: Database ER Diagram (3NF)
# ==========================================
def get_er_diagram_drawing():
    w, h = 468, 230
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "Database Entity-Relationship Diagram (3NF)")
    
    g = Group()
    # Entity Box Helper
    def add_table_box(g, x, y, width, height, title, cols):
        # Header rect
        g.add(Rect(x, y + height - 15, width, 15, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=2, ry=2))
        g.add(String(x + width/2, y + height - 11, title, fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
        # Body rect
        g.add(Rect(x, y, width, height - 15, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_BORDER, rx=2, ry=2))
        
        # Column listings
        cy = y + height - 25
        for col in cols:
            g.add(String(x + 5, cy, col, fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK))
            cy -= 9

    # 1. users
    add_table_box(g, 10, 130, 95, 55, "users", [
        "🔑 username [PK]",
        "• password_hash",
        "• role (student/admin)"
    ])
    
    # 2. appointments
    add_table_box(g, 150, 130, 120, 85, "appointments", [
        "🔑 id [PK]",
        "🔗 student_name [FK]",
        "• advisor_name",
        "• booking_date",
        "• time_slot",
        "• topic",
        "• status"
    ])
    
    # 3. interaction_logs
    add_table_box(g, 150, 20, 120, 95, "interaction_logs", [
        "🔑 id [PK]",
        "🔗 username [FK]",
        "• user_message",
        "• bot_response",
        "• latency_ms",
        "• sentiment_score",
        "• routing_mode",
        "• timestamp"
    ])
    
    # 4. courses
    add_table_box(g, 320, 130, 125, 75, "courses", [
        "🔑 id [PK]",
        "• name",
        "• department",
        "• description",
        "• interests",
        "• duration"
    ])
    
    # 5. policies
    add_table_box(g, 320, 40, 125, 50, "policies", [
        "🔑 id [PK]",
        "• topic",
        "• content"
    ])
    
    # Relations lines (using simple lines with endpoints)
    # users.username (1) -> appointments.student_name (*)
    g.add(Line(105, 155, 150, 155, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(String(112, 158, "1", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE))
    g.add(String(142, 158, "0..*", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE))
    
    # users.username (1) -> interaction_logs.username (*)
    g.add(Line(50, 130, 50, 70, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(Line(50, 70, 150, 70, strokeColor=COLOR_SLATE, strokeWidth=1))
    g.add(String(53, 118, "1", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE))
    g.add(String(138, 73, "0..*", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE))
    
    # Independent database symbols for isolated info tables (courses, policies)
    g.add(String(325, 215, "Static Reference Catalogs", fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_SLATE))
    g.add(Line(320, 210, 445, 210, strokeColor=COLOR_BORDER, strokeWidth=0.5))
    
    d.add(g)
    return d

# ==========================================
# 5. Figure 4.3: UML Class Diagram
# ==========================================
def get_class_diagram_drawing():
    w, h = 468, 180
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "UML Class Interaction Diagram")
    
    g = Group()
    
    # Class Box Helper (3-compartment rectangle)
    def add_class_box(g, x, y, width, height, name, attributes, methods):
        # Header (Name)
        g.add(Rect(x, y + height - 18, width, 18, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=2, ry=2))
        g.add(String(x + width/2, y + height - 12, name, fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
        
        # Compartment rects
        g.add(Rect(x, y, width, height - 18, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_BORDER))
        
        # Division lines
        divider_y = y + height - 18 - (len(attributes) * 10) - 5
        g.add(Line(x, divider_y, x + width, divider_y, strokeColor=COLOR_BORDER, strokeWidth=0.5))
        
        # Attributes
        cy = y + height - 28
        for attr in attributes:
            g.add(String(x + 5, cy, attr, fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK))
            cy -= 10
            
        # Methods
        my = divider_y - 10
        for method in methods:
            g.add(String(x + 5, my, method, fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK))
            my -= 10

    # Class 1: DatabaseManager
    add_class_box(g, 25, 20, 185, 120, "DatabaseManager", [
        "+ engine: Engine",
        "+ SessionLocal: sessionmaker",
        "+ Base: DeclarativeBase"
    ], [
        "+ get_db(): Generator",
        "+ seed_database(session: Session)",
        "+ init_database(): None"
    ])
    
    # Class 2: ChatController
    add_class_box(g, 258, 20, 185, 120, "ChatController", [
        "+ db_session: Session",
        "+ regex_patterns: Dict",
        "+ sentiment_analyzer: TextBlob"
    ], [
        "+ route_query(query: str): Dict",
        "+ match_local_rules(q: str): Object",
        "+ call_puter_ai(prompt: str): str",
        "+ get_sentiment(text: str): float"
    ])
    
    # Association Arrow: ChatController ---uses---> DatabaseManager
    draw_arrow(g, 258, 80, 210, 80, "uses", "top")
    
    d.add(g)
    return d

# ==========================================
# 6. Figure 4.4: Sequence Diagram for Chat Flow
# ==========================================
def get_sequence_diagram_drawing():
    w, h = 468, 225
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "Sequence Diagram for Chat Resolution Flow")
    
    g = Group()
    
    # Lifeline Lifespans
    cols = [40, 135, 230, 325, 420]
    names = ["Student", "Streamlit UI", "ChatController", "Aiven DB", "Puter AI"]
    
    for i, col in enumerate(cols):
        # Header Box
        g.add(Rect(col - 35, 195, 70, 18, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY, rx=2, ry=2))
        g.add(String(col, 201, names[i], fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))
        # Vertical dashed lifeline
        g.add(Line(col, 35, col, 195, strokeColor=COLOR_SLATE, strokeWidth=0.8, strokeDashArray=[3, 3]))
        # Bottom indicator
        g.add(Rect(col - 35, 17, 70, 18, fillColor=COLOR_SLATE, strokeColor=COLOR_SLATE, rx=2, ry=2))
        g.add(String(col, 23, names[i], fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_LIGHT, textAnchor="middle"))

    # Activation blocks (vertical rects on lifelines)
    g.add(Rect(132, 55, 6, 120, fillColor=COLOR_BORDER, strokeColor=COLOR_SLATE, strokeWidth=0.5)) # UI active: covers 55 to 175
    g.add(Rect(227, 70, 6, 90, fillColor=COLOR_BORDER, strokeColor=COLOR_SLATE, strokeWidth=0.5))  # Controller active: covers 70 to 160
    g.add(Rect(322, 130, 6, 15, fillColor=COLOR_BORDER, strokeColor=COLOR_SLATE, strokeWidth=0.5)) # DB check active: covers 130 to 145
    g.add(Rect(417, 100, 6, 15, fillColor=COLOR_BORDER, strokeColor=COLOR_SLATE, strokeWidth=0.5)) # Puter AI active: covers 100 to 115
    g.add(Rect(322, 65, 6, 10, fillColor=COLOR_BORDER, strokeColor=COLOR_SLATE, strokeWidth=0.5))  # DB write active: covers 65 to 75

    # Interaction Steps (Chronological y-coords from top to bottom)
    # y=175: Student -> UI (Submit Query)
    draw_arrow(g, 40, 175, 132, 175, "Submit Query", "top")
    
    # y=160: UI -> Controller (route_query)
    draw_arrow(g, 138, 160, 227, 160, "route_query()", "top")
    
    # y=145: Controller -> DB (Check Local Regex/Facts)
    draw_arrow(g, 233, 145, 322, 145, "RegexMatch()", "top")
    # y=130: DB -> Controller (Return fact/None)
    draw_arrow(g, 322, 130, 233, 130, "Return Fact / None", "bottom")
    
    # y=115: Controller -> Puter AI (Fallback invoke if None)
    draw_arrow(g, 233, 115, 417, 115, "call_puter_ai()", "top")
    # y=100: Puter AI -> Controller (Token response)
    draw_arrow(g, 417, 100, 233, 100, "AI Response", "bottom")
    
    # y=85: Controller -> UI (Format message & state updates)
    draw_arrow(g, 227, 85, 138, 85, "Formatted Text", "bottom")
    
    # y=70: Controller -> DB (Async Log write)
    draw_arrow(g, 233, 70, 322, 70, "LogInteraction()", "top")
    
    # y=55: UI -> Student (Render Chat Bubbles)
    draw_arrow(g, 132, 55, 40, 55, "Show bubbles", "bottom")
    
    d.add(g)
    return d

# ==========================================
# 7. Figure 4.5: System Activity Diagram
# ==========================================
def get_activity_diagram_drawing():
    w, h = 468, 250
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "System Activity Logic Lifecycle Diagram")
    
    g = Group()
    
    # Node Drawing Helpers
    def draw_decision(g, x, y, text):
        # Diamond shape
        g.add(Polygon([x, y+15, x+45, y, x, y-15, x-45, y], fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_SLATE))
        g.add(String(x, y-3, text, fontName="Helvetica-Bold", fontSize=7, fillColor=COLOR_NAVY, textAnchor="middle"))
        
    def draw_process(g, x, y, w, h, text):
        g.add(Rect(x-w/2, y-h/2, w, h, fillColor=COLOR_BG_LIGHT, strokeColor=COLOR_SLATE, rx=3, ry=3))
        g.add(String(x, y-3, text, fontName="Helvetica", fontSize=7, fillColor=COLOR_TEXT_DARK, textAnchor="middle"))

    # Start Node
    g.add(Circle(234, 230, 6, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY))
    g.add(String(234, 240, "Start Session", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_NAVY, textAnchor="middle"))
    
    # Arrow to Decision 1
    draw_arrow(g, 234, 224, 234, 200)
    
    # Decision 1: Attendance/Grading Policy Keyword Match?
    draw_decision(g, 234, 185, "Policy Match?")
    
    # YES Path (Left) -> Fetch Policy Record
    draw_arrow(g, 189, 185, 110, 185, "YES", "top")
    draw_process(g, 60, 185, 100, 24, "Fetch Local Policy")
    
    # NO Path -> Decision 2
    draw_arrow(g, 234, 170, 234, 140, "NO", "left")
    
    # Decision 2: Course short code key Match?
    draw_decision(g, 234, 125, "Course Match?")
    
    # YES Path (Left) -> Fetch Course Catalog
    draw_arrow(g, 189, 125, 110, 125, "YES", "top")
    draw_process(g, 60, 125, 100, 24, "Fetch Course Details")
    
    # NO Path (Right) -> Call Puter Edge AI Fallback API
    draw_arrow(g, 279, 125, 358, 125, "NO", "top")
    draw_process(g, 408, 125, 100, 24, "Call Puter Edge AI")
    
    # Merge paths back to Logger Process
    # Left flows -> Route to x=5 to bypass the process boxes and avoid overlaps
    g.add(Line(10, 185, 5, 185, strokeColor=COLOR_SLATE, strokeWidth=1)) # From Fetch Local Policy left edge
    g.add(Line(10, 125, 5, 125, strokeColor=COLOR_SLATE, strokeWidth=1)) # From Fetch Course Details left edge
    g.add(Line(5, 185, 5, 70, strokeColor=COLOR_SLATE, strokeWidth=1))   # Vertical bypass line
    draw_arrow(g, 5, 70, 184, 70)                                       # Arrow to Log & Render left edge
    
    # Right flows -> Logger
    g.add(Line(408, 113, 408, 70, strokeColor=COLOR_SLATE, strokeWidth=1))
    draw_arrow(g, 408, 70, 284, 70)
    
    # Log & Render Process
    draw_process(g, 234, 70, 100, 24, "Log & Render Response")
    
    # End Node
    draw_arrow(g, 234, 58, 234, 30)
    g.add(Circle(234, 20, 8, fillColor=None, strokeColor=COLOR_NAVY, strokeWidth=1))
    g.add(Circle(234, 20, 5, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY))
    g.add(String(234, 5, "Session Logged", fontName="Helvetica", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    d.add(g)
    return d

# ==========================================
# 8. Figure 7.1: Query Volume Line Graph
# ==========================================
def get_query_volume_chart():
    w, h = 468, 180
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "Query Volume Over Time (June 1 - June 13)")
    
    g = Group()
    
    # Chart configurations (margins: left=45, bottom=30, right=20, top=20)
    cx, cy, cw, ch = 45, 30, 390, 120
    
    # Draw Gridlines and Axes
    g.add(Rect(cx, cy, cw, ch, fillColor=colors.white, strokeColor=COLOR_BORDER, strokeWidth=1))
    
    # Horizontal gridlines (Y-axis intervals of 10 up to 60)
    y_vals = [0, 10, 20, 30, 40, 50, 60]
    for y in y_vals:
        py = cy + (y / 60.0) * ch
        g.add(Line(cx, py, cx + cw, py, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
        # Y labels
        g.add(String(cx - 8, py - 3, str(y), fontName="Helvetica", fontSize=7, fillColor=COLOR_SLATE, textAnchor="end"))
    
    # Y-axis label
    g.add(String(12, cy + ch/2, "Query Volume (Daily Count)", fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # X-Axis Data points (June 1 to June 13)
    dates = ["June 1", "June 3", "June 5", "June 7", "June 9", "June 11", "June 13"]
    # Real data mapping
    data_points = [
        (0.0, 12),  # June 1: 12 queries
        (1.0, 18),  # June 2: 18
        (2.0, 31),  # June 3: 31 (Sprint 2 Deployment)
        (3.0, 26),  # June 4: 26
        (4.0, 35),  # June 5: 35
        (5.0, 22),  # June 6: 22
        (6.0, 19),  # June 7: 19
        (7.0, 24),  # June 8: 24
        (8.0, 38),  # June 9: 38
        (9.0, 42),  # June 10: 42
        (10.0, 48), # June 11: 48 (Sprint 3 Beta)
        (11.0, 52), # June 12: 52
        (12.0, 58)  # June 13: 58 (Final Pilot release)
    ]
    
    # Draw X axis labels (Skip days to prevent overlap)
    for i in range(7):
        px = cx + (i * 2.0 / 12.0) * cw
        g.add(Line(px, cy, px, cy - 3, strokeColor=COLOR_SLATE, strokeWidth=1))
        g.add(String(px, cy - 12, dates[i], fontName="Helvetica", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))
        
    # Plot data line
    prev_x, prev_y = None, None
    for x_idx, val in data_points:
        px = cx + (x_idx / 12.0) * cw
        py = cy + (val / 60.0) * ch
        
        # Draw dot
        g.add(Circle(px, py, 3, fillColor=COLOR_NAVY, strokeColor=COLOR_NAVY))
        
        # Connect line
        if prev_x is not None:
            g.add(Line(prev_x, prev_y, px, py, strokeColor=COLOR_NAVY, strokeWidth=1.5))
            
        prev_x, prev_y = px, py
        
    # Annotations
    # Sprint 2
    px_s2 = cx + (2.0 / 12.0) * cw
    py_s2 = cy + (31 / 60.0) * ch
    g.add(Line(px_s2, py_s2, px_s2, py_s2 + 25, strokeColor=COLOR_SLATE, strokeWidth=0.5, strokeDashArray=[2, 2]))
    g.add(String(px_s2, py_s2 + 28, "Sprint 2 Release (31)", fontName="Helvetica", fontSize=6, fillColor=COLOR_SLATE, textAnchor="middle"))
    
    # Final Pilot
    px_final = cx + (12.0 / 12.0) * cw
    py_final = cy + (58 / 60.0) * ch
    g.add(Line(px_final - 30, py_final - 15, px_final - 5, py_final - 5, strokeColor=COLOR_SLATE, strokeWidth=0.5))
    g.add(String(px_final - 32, py_final - 18, "Final Release (58)", fontName="Helvetica-Bold", fontSize=6, fillColor=COLOR_NAVY, textAnchor="end"))

    d.add(g)
    return d

# ==========================================
# 9. Figure 7.2: Sentiment Bar Chart
# ==========================================
def get_sentiment_chart():
    w, h = 468, 140
    d = Drawing(w, h)
    add_header_footer_to_drawing(d, w, h, "Student Query Sentiment Distribution Breakdown")
    
    g = Group()
    
    # Dimensions: left=55, bottom=20, width=360, height=90
    cx, cy, cw, ch = 55, 20, 360, 90
    
    # Draw outline
    g.add(Rect(cx, cy, cw, ch, fillColor=colors.white, strokeColor=COLOR_BORDER, strokeWidth=0.5))
    
    # X Gridlines (Percentages 0% to 100%, step 20)
    for p in range(0, 101, 20):
        px = cx + (p / 100.0) * cw
        g.add(Line(px, cy, px, cy + ch, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
        g.add(String(px, cy - 10, f"{p}%", fontName="Helvetica", fontSize=7, fillColor=COLOR_SLATE, textAnchor="middle"))

    # Three Categories: Positive (60%), Neutral (25%), Negative (15%)
    cats = ["Positive (60%)", "Neutral (25%)", "Negative (15%)"]
    pcts = [60, 25, 15]
    colors_list = [COLOR_GREEN, COLOR_YELLOW, COLOR_RED]
    
    bar_h = 18
    spacing = 10
    
    # Draw horizontal bars
    for i in range(3):
        # Bar Y start
        by = cy + ch - (i + 1) * (bar_h + spacing)
        # Bar width
        bw = (pcts[i] / 100.0) * cw
        
        # Render bar rectangle
        g.add(Rect(cx, by, bw, bar_h, fillColor=colors_list[i], strokeColor=colors_list[i], rx=1, ry=1))
        
        # Label category
        g.add(String(cx - 8, by + 5, cats[i], fontName="Helvetica-Bold", fontSize=8, fillColor=COLOR_TEXT_DARK, textAnchor="end"))
        
    d.add(g)
    return d
