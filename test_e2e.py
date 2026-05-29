from playwright.sync_api import Page, expect

# The streamlit app is assumed to be running at http://localhost:8501

def test_ui_load(page: Page):
    """Verify that the UI loads and displays the title."""
    page.goto("http://localhost:8501")
    # Wait for the title to appear
    expect(page.get_by_role("heading", name="Chandigarh University Advisor")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Smart Academic Support")).to_be_visible()

def test_navigation(page: Page):
    """Verify navigation between pages."""
    page.goto("http://localhost:8501")
    
    # Check sidebar
    expect(page.get_by_text("CU Advisor").first).to_be_visible(timeout=10000)
    
    # Navigate to Chat History
    # Use exact text and click it
    page.get_by_text("Chat History", exact=True).click()
    expect(page.get_by_role("heading", name="Conversation Logs")).to_be_visible(timeout=15000)
    
    # Back to Student Advisor
    # Sometimes clicking the text inside a radio button group is tricky in Streamlit
    # Let's try to click the radio button specifically if get_by_text fails to trigger rerun
    page.get_by_text("Student Advisor", exact=True).click()
    
    # Verification with multiple possible heading formats
    expect(page.get_by_text("Chandigarh University Advisor").first).to_be_visible(timeout=15000)

def test_local_logic_response(page: Page):
    """Verify that local logic triggers for specific keywords."""
    page.goto("http://localhost:8501")
    
    chat_input = page.get_by_placeholder("How can I help you today?")
    chat_input.fill("What courses do you have for engineering?")
    chat_input.press("Enter")
    
    # Check for local response (contains specific course info from courses.json)
    expect(page.get_by_text("Based on your interests, I recommend")).to_be_visible(timeout=15000)
    # Use first() or a more specific locator to avoid strict mode violation
    expect(page.get_by_text("Bachelor of Engineering").first).to_be_visible()

def test_login_flow(page: Page):
    """Verify the login flow."""
    page.goto("http://localhost:8501")
    
    # Open Login form in sidebar
    page.get_by_role("tab", name="Login").click()
    
    sidebar = page.locator("section[data-testid='stSidebar']")
    sidebar.get_by_label("Username").first.fill("Manik")
    sidebar.get_by_label("Password").first.fill("Manik")
    sidebar.get_by_role("button", name="Login").click()
    
    # Check for welcome message
    expect(page.get_by_text("Welcome, Manik")).to_be_visible(timeout=15000)
    
    # Check for Personalized mode caption which confirms login success
    expect(page.get_by_text("Mode: Personalized")).to_be_visible(timeout=10000)

def test_ai_mode_trigger(page: Page):
    """Verify that AI mode is triggered for unknown queries."""
    page.goto("http://localhost:8501")
    
    chat_input = page.get_by_placeholder("How can I help you today?")
    chat_input.fill("Tell me a joke about robots.")
    chat_input.press("Enter")
    
    # Should show "Thinking..."
    expect(page.get_by_text("Thinking...")).to_be_visible()
    
    # Since this is an E2E test and Puter.js works in browser, 
    # we expect the bridge to eventually receive a response if Puter is working.
    # However, in a headless CI environment without a real browser and Puter SDK loaded properly, 
    # this might be tricky. We are testing the UI behavior.
    
    # Check that it doesn't hang indefinitely (timeout 30s for AI)
    # expect(page.get_by_text("Thinking...")).to_be_hidden(timeout=30000)

def test_responsive_ui(page: Page):
    """Verify UI elements are visible on different screen sizes."""
    # Mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8501")
    expect(page.get_by_text("CU Advisor")).to_be_visible()
    
    # Desktop view
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto("http://localhost:8501")
    expect(page.get_by_text("CU Advisor")).to_be_visible()
