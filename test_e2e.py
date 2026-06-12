import pytest
import socket
from playwright.sync_api import Page, expect

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Skip all tests in this file if Streamlit is not running
pytestmark = pytest.mark.skipif(not is_port_open(8501), reason="Streamlit server not running on port 8501")

def test_ui_load(page: Page):
    """Verify that the UI loads and displays the title."""
    page.goto("http://localhost:8501")
    expect(page).to_have_title("CU AI Advisor")
    expect(page.get_by_text("Chandigarh University Advisor")).to_be_visible()

def test_navigation(page: Page):
    """Verify navigation between pages."""
    page.goto("http://localhost:8501")
    
    # Check default page
    expect(page.get_by_text("How can I assist you today?")).to_be_visible()
    
    # Navigate to History
    page.get_by_label("Navigation").get_by_text("Chat History").click()
    expect(page.get_by_text("Conversation Logs")).to_be_visible()

def test_local_logic_response(page: Page):
    """Verify that local logic triggers for specific keywords."""
    page.goto("http://localhost:8501")
    
    # Type a query that triggers local logic
    chat_input = page.get_by_placeholder("How can I help you today?")
    chat_input.fill("What is the attendance policy?")
    chat_input.press("Enter")
    
    # Check for policy response
    expect(page.get_by_text("According to CU Policy on Attendance")).to_be_visible()

def test_login_flow(page: Page):
    """Verify the login flow."""
    page.goto("http://localhost:8501")
    
    # Logout if already logged in from previous test
    try:
        page.get_by_role("button", name="Logout").click(timeout=1000)
        page.get_by_text("Login").first.wait_for(state="visible", timeout=3000)
    except Exception:
        pass
    
    # Go to Sign Up
    page.get_by_text("Sign Up").first.click()
    
    # Fill signup
    page.get_by_label("New Username", exact=True).fill("test_e2e_user")
    page.get_by_label("New Password", exact=True).fill("password123")
    page.get_by_role("button", name="Create Account").click()
    
    # Try to login
    page.get_by_text("Login").first.click()
    page.get_by_label("Username", exact=True).fill("test_e2e_user")
    page.get_by_label("Password", exact=True).fill("password123")
    page.get_by_role("button", name="Login").click()
    
    # Verify welcome message (using user name instead of "Welcome, ...")
    expect(page.get_by_text("test_e2e_user")).to_be_visible()

def test_ai_mode_trigger(page: Page):
    """Verify that AI mode is triggered for unknown queries."""
    page.goto("http://localhost:8501")
    
    # Type a query that triggers AI
    chat_input = page.get_by_placeholder("How can I help you today?")
    chat_input.fill("What is the capital of France?")
    chat_input.press("Enter")
    
    # Wait for the user message to appear first
    expect(page.get_by_text("What is the capital of France?")).to_be_visible()
    
    # Check for "Thinking..." or the response
    # Sometimes "Thinking..." is very brief
    try:
        expect(page.get_by_text("Thinking...")).to_be_visible(timeout=2000)
    except Exception:
        pass # It might have already moved to response
    
    # Check for AI response content
    expect(page.locator(".stChatMessage").last).to_contain_text("Paris", timeout=20000)

def test_responsive_ui(page: Page):
    """Verify UI elements are visible on different screen sizes."""
    # Mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8501")
    expect(page.get_by_text("CU Advisor")).to_be_hidden() # Sidebar usually collapses
    
    # Desktop view
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto("http://localhost:8501")
    expect(page.get_by_text("CU Advisor")).to_be_visible()

def test_course_recommendations(page: Page):
    """Verify that course recommendations trigger based on user interests."""
    page.goto("http://localhost:8501")
    chat_input = page.get_by_placeholder("How can I help you today?")
    chat_input.fill("suggest a coding course")
    chat_input.press("Enter")
    expect(page.get_by_text("Master of Computer Applications")).to_be_visible()

def test_fashion_course_recommendations(page: Page):
    """Verify that fashion course recommendations trigger based on user interests."""
    page.goto("http://localhost:8501")
    chat_input = page.get_by_placeholder("How can I help you today?")
    chat_input.fill("tell me course for fashion designing")
    chat_input.press("Enter")
    expect(page.get_by_text("Bachelor of Design (B.Des) - Fashion Design")).to_be_visible()

def test_appointment_booking_flow(page: Page):
    """Verify the student appointment booking page, including validation."""
    page.goto("http://localhost:8501")
    
    # Logout if already logged in from previous test
    try:
        page.get_by_role("button", name="Logout").click(timeout=1000)
        page.get_by_text("Login").first.wait_for(state="visible", timeout=3000)
    except Exception:
        pass
        
    # Sign up and login first
    page.get_by_text("Sign Up").first.click()
    page.get_by_label("New Username", exact=True).fill("booking_user")
    page.get_by_label("New Password", exact=True).fill("pass123")
    page.get_by_role("button", name="Create Account").click()
    
    page.get_by_text("Login").first.click()
    page.get_by_label("Username", exact=True).fill("booking_user")
    page.get_by_label("Password", exact=True).fill("pass123")
    page.get_by_role("button", name="Login").click()
    
    # Navigate to Book Appointment
    page.get_by_label("Navigation").get_by_text("Book Appointment").click()
    expect(page.get_by_text("Book Academic Advising Appointment")).to_be_visible()
    
    # Try booking with empty course topic to trigger error
    page.get_by_role("button", name="Book Appointment").click()
    expect(page.get_by_text("Please enter a topic or course of interest.")).to_be_visible()
    
    # Fill out details and book valid session
    page.get_by_placeholder("e.g. Master of Computer Applications").fill("MCA Advising")
    page.get_by_role("button", name="Book Appointment").click()
    
    # Should show Success or Weekend/Timing validation error message cleanly
    expect(page.get_by_text("Success").or_(page.get_by_text("Error"))).to_be_visible()

def test_admin_dashboard_and_analytics(page: Page):
    """Verify that admin dashboard loads and displays analytics correctly."""
    page.goto("http://localhost:8501")
    
    # Logout if already logged in from previous test
    try:
        page.get_by_role("button", name="Logout").click(timeout=1000)
        page.get_by_text("Login").first.wait_for(state="visible", timeout=3000)
    except Exception:
        pass
        
    # Login as bootstrapped admin
    page.get_by_text("Login").first.click()
    page.get_by_label("Username", exact=True).fill("test_admin")
    page.get_by_label("Password", exact=True).fill("admin123")
    page.get_by_role("button", name="Login").click()
    
    # Navigate to Admin Dashboard and check components
    page.get_by_label("Navigation").get_by_text("Admin Dashboard").click()
    expect(page.get_by_text("Advisor Analytics")).to_be_visible()
    expect(page.get_by_text("Total Queries")).to_be_visible()
    
    # Plotly charts container should render
    expect(page.locator("div[data-testid='stPlotlyChart']").first).to_be_visible(timeout=15000)
    
    # Navigate to Appointment Management
    page.get_by_label("Navigation").get_by_text("Appointment Management").click()
    expect(page.get_by_text("Appointment Management")).to_be_visible()
