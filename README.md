# CU AI Advisor (MCA Final Project) - Optimized Version

An AI-powered academic advising chatbot using low-code tools integrated with conversational AI APIs. This project has been refined to professional standards, featuring a modern UI, robust local logic, and advanced analytics.

**GitHub Repository:** [https://github.com/manikbholaji/ai-chatbot](https://github.com/manikbholaji/ai-chatbot)

---

## 🌟 Key Features & Improvements
- **Hybrid AI Architecture**: Combines fast local rule-based matching for university-specific data with advanced generative AI (GPT-4o-mini) for complex queries.
- **Privacy-First & Serverless**: Uses Puter.js for client-side AI processing, requiring NO backend API keys or expensive cloud compute.
- **Enhanced UI/UX**: Professional Streamlit interface with custom CSS, interactive quick-actions, and mobile-responsive design.
- **Advanced Admin Dashboard**: Real-time analytics using Plotly, tracking query volume, user activity, and sentiment analysis.
- **Comprehensive Database**: Structured SQLAlchemy ORM managing Users, Courses, Policies, Interaction Logs, and Appointments.
- **Robust Testing**: Full suite of unit tests and Playwright E2E tests ensuring conversational accuracy and UI stability.

## 🎯 Project Objectives
The objective of this project is to build an AI-powered academic advising chatbot that provides course recommendations, academic planning suggestions, and automated appointment scheduling for Chandigarh University students.

## ✅ Professional Enhancements (v2.0)
1. **Refined Matching Logic**: Improved regex-based matching for programs and policies.
2. **Expanded Knowledge Base**: Added more academic programs and refined policy descriptions.
3. **Data Visualization**: Integrated Plotly charts for admin insights.
4. **Code Quality**: Removed dead code and reorganized project structure for better maintainability.
5. **Session Management**: Added "Clear Chat" and improved logout flows.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit (Python)
- **AI Integration**: Puter.js (Client-Side `gpt-4o-mini`)
- **Database**: SQLAlchemy ORM (SQLite / PostgreSQL)
- **Analytics**: Pandas, Plotly, TextBlob
- **Testing**: Pytest, Playwright

## 📋 Quick Setup

1. **Clone & Install**:
   ```bash
   git clone https://github.com/manikbholaji/ai-chatbot
   cd ai-chatbot
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python database.py
   ```

3. **Run Locally**:
   ```bash
   streamlit run app.py
   ```

4. **Run Tests**:
   ```bash
   pytest
   ```

## 📂 Project Structure
- `app.py`: Main Streamlit UI and Analytics Dashboard.
- `chatbot.py`: Core advisor logic and system prompt configuration.
- `database.py`: Database models and interaction layer.
- `puter_bridge/`: Client-side bridge for secure AI integration.
- `docs/`: Project reports, Viva guides, and presentations.

## 📊 Evaluation Parameters
This project strictly follows professional standards for MCA final semester deliverables, prioritizing privacy-first AI deployment, efficient low-code orchestration, and robust relational data management.
