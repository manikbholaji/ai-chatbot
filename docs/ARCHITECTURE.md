# CU AI Advisor - Chatbot Architecture & API Flow Documentation

This document provides a detailed breakdown of the system architecture, data models, logic routing, and API integration flows for the Chandigarh University AI Advisor application (MCA Final Year Project).

---

## 1. System Architecture Overview

The application is built using a **hybrid serverless-ready architecture** designed for high scalability, rapid response times, and robust relational data management.

```mermaid
graph TD
    User([🎓 Student / Admin]) <--> |HTTP/HTTPS| FE[Streamlit Frontend UI]
    subgraph AppServer [Application Server Layer]
        FE <--> |Local Logic & Sessions| ChatBot[Chatbot Controller]
        ChatBot <--> |SQLAlchemy ORM| DB_Mgr[Database Connection Manager]
    end
    subgraph Data [Data & Storage Layer]
        DB_Mgr <-->|Aiven PostgreSQL / SQLite Fallback| RDBMS[(Relational Database)]
    end
    subgraph ExternalServices [External AI Services]
        ChatBot <--> |REST API / Bearer Token| PuterAPI[Puter AI API: gpt-4o-mini]
    end
```

---

## 2. Hybrid Query Routing Flowchart

The system prioritizes speed and cost efficiency by executing a fast local rule-based match before delegating complex requests to the advanced Large Language Model.

```mermaid
flowchart TD
    Start([User inputs query]) --> Prep[Normalize query to lowercase]
    Prep --> CheckPolicy{Matches local policy / rule?}
    
    CheckPolicy -- Yes --> ReturnLocalPolicy[Return policy info instantly]
    ReturnLocalPolicy --> LogDB[Log interaction to DB & calculate sentiment]
    
    CheckPolicy -- No --> CheckCourse{Matches local course name / interest?}
    
    CheckCourse -- Yes --> ReturnLocalCourse[Return recommended course list]
    ReturnLocalCourse --> LogDB
    
    CheckCourse -- No --> CallAI[Retrieve chat session history]
    CallAI --> AssemblePrompt[Combine System Prompt + History]
    AssemblePrompt --> SendPuter[Send POST request to Puter AI API]
    SendPuter --> ReceiveAI[Receive GPT-4o-mini response]
    ReceiveAI --> LogDB
    
    LogDB --> Render[Render response in chat container]
    Render --> End([Done])
```

---

## 3. Database Entity-Relationship (ER) Model

The application utilizes SQLAlchemy ORM to manage user sessions, academic programs, university guidelines, feedback sentiment tracking, and booking schedules.

```mermaid
erDiagram
    users {
        string username PK
        string password_hash
        string role
    }
    courses {
        string id PK
        string name
        string department
        text description
        text interests
        string duration
    }
    policies {
        int id PK
        string topic
        text description
    }
    interaction_logs {
        int id PK
        datetime timestamp
        string user
        string mode
        text student_message
        text bot_response
        float sentiment
    }
    appointments {
        int id PK
        string student_name
        string course_name
        string date
        string time
        datetime timestamp
    }
```

---

## 4. API & Interaction Sequence Diagram

The diagram below details the sequence of operations from the moment a student types a query until the advisor returns the finalized answer.

```mermaid
sequenceDiagram
    autonumber
    actor Student as 🎓 Student
    participant UI as Streamlit UI
    participant Chat as Chatbot Controller
    participant DB as Relational DB
    participant Puter as Puter AI (gpt-4o-mini)

    Student->>UI: Types query ("Suggest a course for fashion designing")
    UI->>Chat: get_local_response("suggest fashion design...")
    Chat->>DB: Query courses & policies cache
    DB-->>Chat: Returns courses data
    Note over Chat: Checks local interests list.<br/>Found matching ID: b_des_fashion
    Chat-->>UI: Returns recommendation response
    UI-->>Student: Renders course list card
    
    Note over Student, UI: If no local match occurs (e.g. "Explain the capital of France")
    
    Student->>UI: Types query ("What is the capital of France?")
    UI->>Chat: get_local_response("capital of France...")
    Note over Chat: No local keywords match courses or policies
    Chat-->>UI: Returns None
    UI->>UI: Shows "Thinking..." spinner
    UI->>Chat: get_ai_response(session_history)
    Chat->>Puter: HTTP POST with Bearer Token (History + Prompt)
    Puter-->>Chat: HTTP JSON Response ("Paris")
    Chat-->>UI: Returns AI response text
    UI->>DB: Log interaction & sentiment (Anonymous, AI-Client, 0.0)
    UI-->>Student: Renders AI response text
```

---

## 5. Security & Deployment Architecture

- **Token Protection**: Puter AI API credentials (`PUTER_TOKEN`) and database connections (`DATABASE_URL`) are stored securely using **Streamlit Secrets** (never committed to git).
- **Graceful DB Fallbacks**: If the cloud-hosted database (Aiven PostgreSQL) encounters connection timeouts or host resolution failures, the database engine falls back dynamically to a local thread-safe **SQLite** file.
