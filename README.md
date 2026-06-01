# CU AI Advisor (MCA Final Project)

An AI-powered academic advising chatbot using low-code tools integrated with conversational AI APIs. The system provides course recommendations, academic planning suggestions, and automated appointment scheduling for Chandigarh University students.

**GitHub Repository:** [https://github.com/manikbholaji/ai-chatbot](https://github.com/manikbholaji/ai-chatbot)

---

## 🎯 Project Objectives
The objective of this project is to build an AI-powered academic advising chatbot using low-code tools integrated with conversational AI APIs. The system provides course recommendations, academic planning suggestions, and automated appointment scheduling.

## ✅ Project Tasks Completed

1. **Integrate chatbot API (OpenAI/Dialogflow):** Integrated OpenAI's `gpt-4o-mini` conversational API seamlessly via the Puter.js serverless SDK.
2. **Design knowledge base for academic policies:** Developed a structured SQL relational database (`Policies` table) and JSON knowledge base to serve instant policy lookups.
3. **Develop course recommendation logic:** Implemented intelligent pattern matching in `chatbot.py` to recommend over 150+ academic programs based on student interests.
4. **Implement chatbot interface within low-code app:** Designed and deployed the chatbot interface using **Streamlit**, a premier low-code Python framework.
5. **Configure appointment booking integration:** Configured an automated transactional booking module in `database.py` for students to schedule consultations with human advisors.
6. **Build student interaction analytics dashboard:** Built a dedicated Admin UI panel in Streamlit that visualizes interaction logs and usage metrics.
7. **Implement sentiment analysis for feedback:** Integrated **TextBlob** to perform real-time sentiment analysis on student queries, logging emotional feedback scores directly into the database.
8. **Conduct conversational accuracy testing:** Conducted rigorous automated unit, integration, and E2E testing suites using **Pytest** and **Playwright**.
9. **Document chatbot architecture and API flow:** Thoroughly documented the 3-Tier Distributed architecture, SQL schema, and async API flow in the 79-page `CU_AI_Advisor_Project_Report.pdf`.
10. **Demonstrate live chatbot interaction:** Deployed via Streamlit Community Cloud for a zero-configuration, live interactive demonstration.

---

## 🚀 100% Serverless & Keyless AI
This app uses a cutting-edge **Client-Side AI Architecture**. Unlike traditional AI apps, this version **requires NO backend API Keys** (`OPENAI_API_KEY`, etc.) and no backend compute configuration for the LLM. All AI processing is handled strictly by the user's browser using the Puter.js Cloud SDK, which communicates directly with OpenAI.

## 🛠️ Tech Stack
- **Frontend / Low-Code Interface**: Streamlit
- **Conversational API Integration**: Puter.js (Client-Side `gpt-4o-mini` / OpenAI)
- **Database / Knowledge Base**: SQLAlchemy ORM (SQLite / PostgreSQL)
- **Analytics & Sentiment**: Pandas, Plotly, TextBlob
- **Testing**: Pytest, Playwright (E2E Conversational Accuracy)

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

4. **Run Conversational Accuracy Tests**:
   ```bash
   pytest
   ```

## 📂 Project Structure
- `app.py`: Main Streamlit low-code UI, Analytics Dashboard, and "Headless" AI Bridge orchestration.
- `puter_bridge/`: The core client-side engine that handles the OpenAI API integration securely.
- `chatbot.py`: Course recommendation logic and local rule-based advisor logic.
- `database.py`: SQLAlchemy ORM models for Policies, Courses, Interactions, and Appointments.
- `CU_AI_Advisor_Project_Report.pdf`: Comprehensive documentation of the architecture and API flow.

## 📊 Evaluation Parameters
This project strictly follows professional standards for MCA final semester deliverables, prioritizing privacy-first AI deployment, efficient low-code orchestration, and robust relational data management.
