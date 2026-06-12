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
    except:
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
