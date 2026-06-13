# CU AI Advisor (MCA Final Project) - Optimized Version

An AI-powered academic advising chatbot using low-code tools integrated with conversational AI APIs. This project has been refined to professional standards, featuring a modern UI, robust local logic, and advanced analytics.

**GitHub Repository:** [https://github.com/manikbholaji/ai-chatbot](https://github.com/manikbholaji/ai-chatbot)

---

## 🌟 Key Features & Improvements
- **Hybrid AI Architecture**: Combines fast local rule-based matching with strict academic intent filtering for university-specific data, falling back to advanced generative AI (GPT-4o-mini) for complex/conversational queries.
- **Smarter Local Interception**: Re-engineered parser prevents keyword over-matching on general queries (e.g. computer jokes) and lets them flow to the AI flawlessly.
- **Privacy-First & Serverless**: Uses Puter.js for client-side AI processing, requiring NO backend API keys or expensive cloud compute.
- **Resilient UI Fallback**: Outage-resilient design displays friendly advising assistant bubbles instead of red error boxes during Puter AI connection issues.
- **Enhanced UI/UX**: Professional Streamlit interface with custom CSS, interactive quick-actions, and mobile-responsive design.
- **Advanced Admin Dashboard**: Real-time analytics using Plotly, tracking query volume, user activity, and sentiment analysis.
- **Cloud-Ready database**: Structured SQLAlchemy ORM supporting both SQLite local fallback and Aiven PostgreSQL with automatic `sslmode=require` injection.
- **Robust DB Seeding**: Upsert-based database initialization guarantees all 12 course offerings (including B.Des Fashion Design) are populated and up to date.
- **Robust Testing**: Full suite of 23 unit and Playwright E2E browser tests ensuring conversational accuracy, database integrity, and UI stability.

## 🎯 Project Objectives
The objective of this project is to build an AI-powered academic advising chatbot that provides course recommendations, academic planning suggestions, and automated appointment scheduling for Chandigarh University students.

## ✅ Professional Enhancements (v4.0)
1. **Smart Intent-Based Interception**: Restructured the chatbot local routing logic to prevent false-positive keyword recommendations.
2. **Aiven PostgreSQL SSL Support**: Programmed automatic SSL query parameter inclusion (`sslmode=require`) to resolve connection drops.
3. **Database Upsert Migration**: Replaced naive seeding checks with full upsert capability to support complete database synchronization.
4. **Outage Resilient UX**: Designed friendly chat fallbacks for API network connection drops.
5. **Data Visualization**: Integrated Plotly charts for real-time admin insights.
6. **Session & State Management**: Added "Clear Chat" and improved logout flows.
7. **Academic Project Report Compilation**: Developed a multi-pass ReportLab-based PDF builder (`build_report.py`) producing a strictly compliant **99-page project report** with clickable index directories and zero margin overflows.
8. **Vector Diagram Alignments**: Re-engineered system drawings (`drawings.py`) to eliminate line crossings, align sequence lifespans, and improve DFD clarity.

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
- `build_report.py`: Multi-pass PDF compilation pipeline utilizing custom canvas templates.
- `drawings.py`: High-quality vector graphics (UML, DFDs, charts) rendered dynamically using ReportLab shape flowables.
- `CU_AI_Advisor_MCA_Final_Report_Manik_Bhola.pdf`: The compiled, university-compliant 99-page project report.
- `docs/ARCHITECTURE.md`: Technical documentation of system architecture, database ER diagram, and query API flow.

## 📊 Evaluation Parameters
This project strictly follows professional standards for MCA final semester deliverables, prioritizing privacy-first AI deployment, efficient low-code orchestration, and robust relational data management.
