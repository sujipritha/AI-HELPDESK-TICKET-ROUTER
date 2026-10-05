# 🤖 AI Helpdesk Ticket Router

An AI-powered helpdesk ticket routing system built with **Python and Streamlit**. The application understands incoming support tickets, identifies their category and priority, routes them to the appropriate department, and provides suggested resolutions using a knowledge base.

## 🚀 Features

* 🎫 **Ticket Classification** — Identifies the type/category of incoming tickets.
* 🚨 **Priority Detection** — Detects whether a ticket is low, medium, high, or critical priority.
* 🏢 **Department Routing** — Automatically routes tickets to the appropriate support team.
* 📚 **Knowledge Base Lookup** — Finds relevant information and suggests possible resolutions.
* 📝 **Ticket Summary** — Generates a concise summary of the customer's issue.
* 📊 **Routing Log** — Maintains a record of ticket classification, priority, and routing decisions.
* 🎨 **Streamlit UI** — User-friendly helpdesk interface with a light-purple sidebar and ticket-router themed design.

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **LLM API**
* **Vector Database**
* **Knowledge Base**
* **AI/NLP**

## 🔄 How It Works

```text
Customer Ticket
      ↓
AI Ticket Analysis
      ↓
Category + Priority Detection
      ↓
Department Routing
      ↓
Knowledge Base Lookup
      ↓
Suggested Resolution
      ↓
Ticket Summary & Routing Log
```

## 📂 Project Structure

```text
AI_Helpdesk_Ticket_Router/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── knowledge_base.json
│
└── assets/
    └── images/
```

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project

```bash
cd AI_Helpdesk_Ticket_Router
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔐 API Key

If the project uses an API key, store it securely using environment variables or Streamlit secrets.

**Do not upload API keys or `.env` files containing secrets to GitHub.**

## 🎯 Project Objective

The goal of this project is to reduce manual helpdesk workload by using AI to understand customer issues, determine their urgency, route them to the correct department, and provide useful resolution suggestions.

## 👩‍💻 Author

**Sujipritha M**

AI & Automation Enthusiast | Python | Streamlit | A
