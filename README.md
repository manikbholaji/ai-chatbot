# AI chatbot (MCA Final Project)

A 100% Client-Side, Keyless, and Anonymous AI academic advising system built for Chandigarh University students.

## 🚀 100% Serverless & Keyless AI
This app uses a cutting-edge **Client-Side AI Architecture**. Unlike traditional AI apps, this version **requires NO API Keys** (`OPENAI_API_KEY`, etc.) and no backend configuration. All AI processing is handled strictly by the user's browser using the Puter.js Cloud SDK.

## 🌟 Features
- **Anonymous AI Usage**: Anyone can use the AI advisor immediately without signing up.
- **Personalized Mode**: Sign in with Google (via Puter) to unlock your name in interaction logs and persistent chat history.
- **Zero-Config Deployment**: Works instantly on Streamlit Community Cloud without adding Secrets or Environment Variables.
- **Hybrid Logic**: Instantly looks up CU courses and policies locally before consulting the AI for complex queries.

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **AI Driver**: Puter.js (Client-Side `gpt-4o-mini`)
- **Analytics**: Pandas, Plotly, TextBlob
- **Data Storage**: Local JSONL (Interactions) & Browser KV (Preferences)

## 📋 Quick Setup

1. **Clone & Install**:
   ```bash
   git clone <your-github-repo-url>
   cd my-gemini-app
   pip install -r requirements.txt
   ```

2. **Run Locally**:
   ```bash
   streamlit run app.py
   ```

## 🌐 Deploy on Streamlit Cloud
1. Push this repository to GitHub.
2. Connect to [Streamlit Community Cloud](https://share.streamlit.io/).
3. **Important**: You do **NOT** need to add any secrets. Just hit Deploy!
4. The app will automatically use the visitor's browser to power the AI.

## 📂 Project Structure
- `app.py`: Main UI and "Headless" AI Bridge orchestration.
- `puter_bridge/`: The core client-side engine that handles Auth and AI.
- `chatbot.py`: Knowledge base and local rule-based advisor logic.
- `data/`: Course information and interaction logs.

## 📊 MCA Final Semester Project
Developed as a final semester project for Master of Computer Applications (MCA). Focuses on cost-effective, privacy-first AI deployment.
