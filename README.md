# AI-Powered E-Commerce Shopping & Recommendation Assistant

An AI-powered e-commerce shopping and product recommendation assistant built with Python and FastAPI.

The goal of this project is to build a production-style intelligent shopping assistant that can understand user preferences, search product information, generate personalized recommendations, and provide conversational shopping assistance.

---

## 🚀 Project Status

**Current Phase:** Phase 1 — Project Setup & Backend Foundation

### Completed

- Python 3.11 development environment
- Python virtual environment
- FastAPI backend
- Uvicorn development server
- Modular project structure
- Health-check API
- Interactive FastAPI documentation
- Git version control
- GitHub repository
- Environment variable template
- Dependency management with `requirements.txt`

### Coming Next

- PostgreSQL database
- Product data models
- Product catalog APIs
- Recommendation engine
- Embeddings and semantic search
- Azure AI Search
- Azure OpenAI
- LangGraph agent workflow
- Personalized shopping assistant
- Automated tests
- Docker containerization

---

## 🎯 Project Goal

The application is designed to provide an intelligent shopping experience by combining:

- Product catalog data
- User preferences
- Semantic search
- Machine learning
- Large language models
- Retrieval-Augmented Generation (RAG)
- Agentic AI workflows
- Personalized recommendations

The final system will allow users to interact with the application conversationally and receive relevant product recommendations based on their needs and preferences.

---

## 🏗️ Planned Architecture

```text
                    User
                     |
                     v
              FastAPI Backend
                     |
                     v
            Shopping Assistant
                     |
          +----------+----------+
          |                     |
          v                     v
    Product Search       Recommendation Engine
          |                     |
          v                     v
   Azure AI Search       ML / Embeddings
          |                     |
          +----------+----------+
                     |
                     v
                LangGraph
                     |
                     v
               Azure OpenAI
                     |
                     v
             Personalized Response


🛠️ Technology Stack
Backend
Python 3.11
FastAPI
Uvicorn
Database
PostgreSQL
AI / Machine Learning
PyTorch
Embeddings
Semantic Search
Recommendation Systems
Retrieval-Augmented Generation (RAG)
Generative AI
Azure OpenAI
LangGraph
Search
Azure AI Search
DevOps
Docker
Git
GitHub
Testing
pytest



ai-ecommerce-shopping-assistant/
│
├── app/
│   ├── api/
│   │   └── __init__.py
│   │
│   ├── core/
│   │   └── __init__.py
│   │
│   ├── db/
│   │   └── __init__.py
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── data/
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md