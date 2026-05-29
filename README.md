# AI chatbot

An AI-powered academic advising system built for Chandigarh University students. This project provides course recommendations based on student interests, academic policy information, and automated appointment scheduling.

## 🚀 Features

- **AI Chatbot**: Powered by OpenAI GPT-4o for intelligent, context-aware conversations.
- **Course Recommendations**: Suggests CU courses based on student interests and goals.
- **Automated Appointments**: Checks for availability (9 AM - 5 PM, Mon-Fri) and schedules advising sessions.
- **Admin Dashboard**: Visualizes student interaction analytics, sentiment trends, and upcoming appointments.
- **Sentiment Analysis**: Tracks student mood and feedback sentiment during interactions.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Engine**: OpenAI API (Function Calling)
- **Analytics**: Pandas, Plotly, TextBlob
- **Data Storage**: Local JSON (for prototyping)

## 📋 Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-github-repo-url>
   cd my-gemini-app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## 🌐 Deploy on Streamlit Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud and choose **New app**.
3. Select the GitHub repository, set the branch, and use `app.py` as the main file.
4. Add `OPENAI_API_KEY` and, if needed, `PUTER_AUTH_TOKEN` in the app secrets or environment settings.
5. Deploy the app. The Streamlit page title is set to **AI chatbot**.

## 📂 Project Structure

- `app.py`: Main Streamlit application UI and dashboard logic.
- `chatbot.py`: Core AI logic, OpenAI integration, and function calling.
- `data/`: Knowledge base and local storage for logs/appointments.
- `requirements.txt`: Project dependencies.

## 📊 MCA Final Semester Project
Developed as a final semester project for Master of Computer Applications (MCA).
