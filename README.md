# 🛒 AI-Powered E-Commerce Shopping & Recommendation Assistant

[![Live Demo](https://img.shields.io/badge/Live%20Demo-trycloudflare.com-success?style=for-the-badge&logo=cloudflare)](https://claims-java-ceremony-restrict.trycloudflare.com/demo/)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-blue?style=for-the-badge&logo=render)](https://render.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](k8s/)
[![Tests](https://img.shields.io/badge/Tests-118%20Passing-brightgreen?style=for-the-badge&logo=pytest)](https://github.com/anvithayerneni/ai-ecommerce-shopping-assistant)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-orange?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

> 🌐 **Live Demo Web Interface:** [https://claims-java-ceremony-restrict.trycloudflare.com/demo/](https://claims-java-ceremony-restrict.trycloudflare.com/demo/)  
> 📖 **Interactive API Docs (Swagger):** [https://claims-java-ceremony-restrict.trycloudflare.com/docs](https://claims-java-ceremony-restrict.trycloudflare.com/docs)  
> 🏥 **Health Check:** [https://claims-java-ceremony-restrict.trycloudflare.com/health](https://claims-java-ceremony-restrict.trycloudflare.com/health)

An AI-powered conversational shopping assistant that combines **semantic product search, deterministic filtering, product reranking, agentic tool calling, product comparison, conversational memory, and grounded LLM responses**.

The project is designed as an end-to-end AI/ML backend system rather than a simple LLM chatbot. Product recommendations are grounded in a structured product catalog, while deterministic application logic is responsible for enforcing important constraints such as price, category, rating, and use case.

---

## 🚀 Live Demo & Deployment

| Resource | Link | Description |
| :--- | :--- | :--- |
| **Live Web App** | [Live Shopping Assistant](https://claims-java-ceremony-restrict.trycloudflare.com/demo/) | Interactive web UI with natural language product search |
| **API Health** | [/health](https://claims-java-ceremony-restrict.trycloudflare.com/health) | Backend health verification endpoint |
| **Swagger API Docs** | [/docs](https://claims-java-ceremony-restrict.trycloudflare.com/docs) | OpenAPI interactive documentation and test console |
| **Kubernetes Architecture** | [`k8s/` manifests](k8s/) | Production cloud-native deployment with HPA autoscaling, Ingress, and Secrets |
| **Render Blueprint** | [`render.yaml`](file:///Users/anvithayerneni/.gemini/antigravity/scratch/ai-ecommerce-shopping-assistant/render.yaml) | 1-click zero-cost deployment configuration for Render |

---

## 🚀 Project Status

**Status: Completed**

The core recommendation and conversational shopping workflow is implemented and covered by an automated test suite.

### Current Implementation

- FastAPI backend
- PostgreSQL product catalog
- Neon PostgreSQL deployment-compatible database
- Azure AI Search
- Vector/semantic product search
- Pre-generated product embeddings
- Deterministic product filtering
- Product reranking
- Natural-language query understanding
- LangGraph shopping workflow
- Azure OpenAI integration
- Agentic tool calling
- Product comparison
- Product-name resolution
- Conversational follow-up handling
- Short-term conversation memory
- Grounded response generation
- Product attribute grounding
- Automated testing
- **118 passing tests**
- Docker & Docker Compose configuration
- Kubernetes cloud-native manifests & autoscaling (`k8s/`)
- Streamlit frontend

---

# 🎯 Project Goal

Traditional e-commerce search often relies heavily on keyword matching and manually selected filters.

This project explores how an AI-powered shopping assistant can combine:

1. Natural-language understanding
2. Semantic search
3. Structured filtering
4. Recommendation ranking
5. Agentic tool usage
6. Conversational context
7. Grounded response generation

to provide a more natural shopping experience.

For example, instead of selecting multiple filters, a user can simply ask:

> "I need a laptop under $1000 for programming."

The system interprets the request, retrieves relevant products, applies deterministic constraints, ranks the results, and generates a grounded response.

---

# ✨ Key Features

## 🔎 Natural-Language Product Search

Users can search for products using natural language.

Examples:

```text
laptop under $1000 for programming
running shoes for training
headphones with good ratings
```

The query-understanding layer extracts structured constraints such as:

- Product category
- Use case
- Minimum price
- Maximum price
- Minimum rating

---

## 🧠 Semantic Product Search

Product queries can be converted into embeddings and used with **Azure AI Search vector search**.

This allows the system to retrieve products based on semantic similarity instead of depending entirely on exact keyword matches.

The embedding layer uses:

```text
all-MiniLM-L6-v2
```

Product embeddings can be generated offline and persisted in:

```text
data/product_embeddings.json
```

This avoids repeatedly generating embeddings for every catalog product.

---

# 🎯 Deterministic Filtering

Important shopping constraints are enforced programmatically rather than relying entirely on an LLM.

Supported constraints include:

- Category
- Minimum price
- Maximum price
- Minimum rating
- Use case

For example:

```text
laptop under $1000
```

is converted into a structured price constraint and enforced by application logic.

This helps prevent the LLM from recommending products that violate explicit user requirements.

---

# 📊 Product Reranking

Retrieved products are reranked using product relevance signals.

The system separates:

```text
Retrieval
    ↓
Filtering
    ↓
Reranking
    ↓
Recommendation
```

This separation allows retrieval and business-rule enforcement to remain deterministic and testable.

---

# 🤖 Agentic Tool Calling

The shopping assistant uses an agentic workflow to interact with product-related tools.

The agent can use tools for tasks such as:

- Searching the product catalog
- Retrieving product information
- Filtering products
- Comparing products

The LLM does not need to directly invent product information.

Instead, authoritative catalog data is retrieved through application tools.

---

# ⚖️ Product Comparison

Users can compare products using natural language.

Example:

```text
Compare MacBook Air M3 and Galaxy Book4
```

The comparison system can evaluate:

- Product name
- Brand
- Category
- Price
- Rating
- Features
- Target audience
- Use cases
- Cheapest product
- Highest-rated product
- Supported use cases

### Example Comparison Reasoning

```text
MacBook Air M3

- Programming explicitly listed as a use case
- Rating: 4.8
- Price: $999.99
```

```text
Galaxy Book4

- Programming not explicitly listed as a use case
- Rating: 4.4
- Price: $849.99
```

The system does not automatically infer that a product supports a capability simply because the product belongs to a particular category.

---

# 🎯 Grounded Product Responses

A major design goal of the project is reducing product-related hallucinations.

The assistant follows explicit grounding rules.

## Grounding Principles

- Only use features explicitly listed for an individual product.
- Only use use cases explicitly listed for an individual product.
- Never combine use cases from different products.
- Never combine features from different products.
- A missing use case means the catalog does not confirm that capability.
- Do not infer capabilities from product category.
- Do not infer capabilities from product brand.
- Do not infer capabilities from product price.
- Do not infer capabilities from product rating.
- Do not infer capabilities from target audience.
- Do not infer capabilities from product name.

### Example

If the catalog contains:

```text
MacBook Air M3
use_cases = programming, studying, office work
```

but:

```text
Galaxy Book4
use_cases = office work, studying, browsing, productivity
```

the assistant does **not** claim that Galaxy Book4 supports programming.

The absence of programming from the Galaxy Book4's catalog data means the system cannot confirm programming as a supported use case.

This distinction is enforced through application logic and grounding rules rather than relying on the LLM alone.

---

# 💬 Conversational Follow-Ups

The system maintains short-term conversational state using **LangGraph**.

This allows users to ask follow-up questions without repeating the original request.

### First Request

```text
I need a laptop under $1000 for programming
```

The system can recommend:

```text
MacBook Air M3
```

### Follow-Up

```text
show me cheaper ones
```

The system resolves the follow-up against the previous shopping context and can return:

```text
Galaxy Book4 — $849.99
```

Other supported conversational examples include:

```text
show me more expensive ones
```

```text
show me Windows ones
```

```text
which one is better for programming?
```

The conversational state allows the assistant to interpret references such as:

- "ones"
- "cheaper"
- "more expensive"
- "which one"

using the context of the previous shopping interaction.

---

# 🧠 Conversational Workflow

The shopping workflow uses **LangGraph** to coordinate the different stages of the assistant.

## High-Level Flow

```text
User Query
    │
    ▼
FastAPI API
    │
    ▼
Shopping Assistant
    │
    ▼
Query Understanding
    │
    ▼
Resolve Follow-Up
    │
    ▼
LangGraph Workflow
    │
    ├───────────────┐
    ▼               ▼
Shopping Agent   Product Search
    │               │
    ▼               ▼
Tool Calling    Azure AI Search
    │               │
    ▼               ▼
Product Tools   Vector Search
    │               │
    └───────┬───────┘
            ▼
   Deterministic Filtering
            │
            ▼
        Reranking
            │
            ▼
     Recommendations
            │
            ▼
   Grounding Validation
            │
            ▼
       Azure OpenAI
            │
            ▼
      Final Response
```

---

# 🏗️ Architecture

```text
                         ┌────────────────────┐
                         │       User         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │     FastAPI        │
                         │       API          │
                         └─────────┬──────────┘
                                   │
                                   ▼
                    ┌───────────────────────────┐
                    │   Shopping Assistant      │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    Query Understanding    │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     LangGraph Workflow    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌─────────────────┐        ┌─────────────────┐
          │ Shopping Agent  │        │ Product Search  │
          └────────┬────────┘        └────────┬────────┘
                   │                          │
                   ▼                          ▼
          ┌─────────────────┐        ┌─────────────────┐
          │ Product Tools   │        │ Azure AI Search │
          └────────┬────────┘        └────────┬────────┘
                   │                          │
                   ▼                          ▼
          ┌─────────────────┐        ┌─────────────────┐
          │ PostgreSQL      │        │ Vector Search   │
          │ Catalog         │        │ + Embeddings    │
          └────────┬────────┘        └────────┬────────┘
                   │                          │
                   └────────────┬─────────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Deterministic       │
                     │ Filtering           │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Product Reranking   │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Recommendation      │
                     │ Generation          │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Grounding           │
                     │ Validation          │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Azure OpenAI        │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Final Response      │
                     └─────────────────────┘
```

---

# 🧩 Technical Design

## Separation of Deterministic and Generative Logic

The system intentionally separates **deterministic application logic** from **LLM-generated content**.

### Deterministic Responsibilities

Python/application logic handles:

- Price constraints
- Category constraints
- Rating constraints
- Use-case filtering
- Product ranking
- Product comparison
- Product grounding
- Product-name resolution
- Conversation-state handling

### LLM Responsibilities

The LLM is primarily used for:

- Natural-language interpretation
- Conversational interaction
- Agentic tool selection
- Final response generation

This architecture reduces the amount of critical business logic delegated to the LLM.

---

# 📁 Project Structure

```text
ai-ecommerce-shopping-assistant/
│
├── app/
│   ├── agents/
│   │   ├── agent_node.py
│   │   ├── shopping_agent.py
│   │   └── shopping_graph.py
│   │
│   ├── api/
│   │   ├── assistant.py
│   │   └── products.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   └── product.py
│   │
│   ├── schemas/
│   │   ├── assistant.py
│   │   ├── product.py
│   │   └── search.py
│   │
│   ├── services/
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── product_ranking.py
│   │   ├── product_service.py
│   │   ├── query_understanding.py
│   │   ├── recommendation_content.py
│   │   ├── recommendation_features.py
│   │   ├── recommendation_metrics.py
│   │   ├── recommendation_model.py
│   │   ├── recommendation_representation.py
│   │   ├── recommendation_service.py
│   │   ├── recommendation_similarity.py
│   │   ├── search_service.py
│   │   ├── shopping_assistant.py
│   │   └── vector_search.py
│   │
│   └── tools/
│       ├── product_compare.py
│       ├── product_details.py
│       ├── product_filter.py
│       ├── product_search.py
│       └── shopping_tools.py
│
├── data/
│   ├── product_embeddings.json
│   ├── products_for_embedding.json
│   ├── recommendation_eval.json
│   └── retrieval_eval.json
│
├── scripts/
│   ├── create_search_index.py
│   ├── enrich_product_metadata.py
│   ├── enrich_products.py
│   ├── evaluate_category_classifier.py
│   ├── evaluate_recommendations.py
│   ├── evaluate_retrieval.py
│   ├── export_products_for_embedding.py
│   ├── generate_product_embeddings.py
│   ├── import_real_products.py
│   ├── index_products_to_azure.py
│   ├── normalize_real_products.py
│   ├── profile_real_dataset.py
│   ├── rollback_enrichment.py
│   ├── seed_products.py
│   ├── semantic_category_classifier.py
│   ├── test_azure_search.py
│   └── test_azure_vector_search.py
│
├── tests/
│   ├── test_assistant_api.py
│   ├── test_db_connection.py
│   ├── test_export_products.py
│   ├── test_main.py
│   ├── test_product_compare.py
│   ├── test_product_comparison.py
│   ├── test_product_enrichment.py
│   ├── test_product_ranking.py
│   ├── test_products.py
│   ├── test_query_understanding.py
│   ├── test_recommendation_content.py
│   ├── test_recommendation_features.py
│   ├── test_recommendation_metrics.py
│   ├── test_recommendation_model.py
│   ├── test_recommendation_representation.py
│   ├── test_recommendation_service.py
│   ├── test_recommendation_similarity.py
│   ├── test_search_api.py
│   ├── test_search_text.py
│   ├── test_shopping_assistant.py
│   ├── test_shopping_graph_memory.py
│   └── test_vector_search.py
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── ui/
│   └── streamlit_app.py
│
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── alembic.ini
├── .env.example
└── README.md
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application and ML logic |
| FastAPI | REST API |
| PostgreSQL | Product catalog and persistence |
| Neon PostgreSQL | Cloud PostgreSQL deployment |
| Azure AI Search | Semantic/vector product retrieval |
| Azure OpenAI | LLM-powered reasoning and response generation |
| LangGraph | Stateful agent workflow |
| LangChain OpenAI | LLM/agent integration |
| Sentence Transformers | Text embeddings |
| PyTorch | Underlying ML framework for embeddings |
| SQLAlchemy | Database ORM |
| Alembic | Database migrations |
| Pydantic | Data validation |
| pytest | Automated testing |
| Streamlit | Interactive frontend |
| Docker | Containerization |
| GitHub | Source control |

---

# 🔌 API

## Health Check

### Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

---

## Root Endpoint

### Endpoint

```http
GET /
```

Example response:

```json
{
  "message": "AI E-Commerce Shopping Assistant API",
  "version": "0.1.0"
}
```

---

## Product Recommendations

### Endpoint

```http
GET /assistant/recommend
```

Example:

```bash
curl "http://127.0.0.1:8000/assistant/recommend?q=I%20need%20a%20laptop%20under%20%241000%20for%20programming&top_k=5"
```

Example response:

```text
Here’s a laptop that fits your request
(under $1000 for programming):

MacBook Air M3 — $999.99

Matches programming:
Programming is explicitly listed as a use case.

Within budget:
$999.99 is within the $1000 limit.
```

---

# 💡 Example Queries

### Budget + Use Case

```text
I need a laptop under $1000 for programming
```

### Follow-Up

```text
show me cheaper ones
```

### Operating System

```text
show me Windows ones
```

### Comparison

```text
compare MacBook Air M3 and Galaxy Book4
```

### Recommendation Reasoning

```text
which one is better for programming?
```

### General Product Search

```text
show me laptops
```

---

# 🧪 Example Conversation

```text
User:
I need a laptop under $1000 for programming

Assistant:
MacBook Air M3 — $999.99

Programming is explicitly listed as a use case.
The product is within the $1000 budget.
```

Then:

```text
User:
show me cheaper ones
```

The assistant resolves the follow-up against the previous shopping context:

```text
Galaxy Book4 — $849.99
```

Then:

```text
User:
show me Windows ones
```

The system can resolve the request against the available catalog data and return the matching Windows product.

---

# 🧪 Testing

The project includes a comprehensive automated test suite covering:

- API endpoints
- Database connectivity
- Product retrieval
- Product filtering
- Product ranking
- Product comparison
- Query understanding
- Recommendation content
- Recommendation features
- Recommendation metrics
- Recommendation model
- Recommendation similarity
- Search behavior
- Vector search
- Shopping assistant behavior
- LangGraph conversation memory

## Running Tests

```bash
pytest
```

## Current Test Suite

```text
118 passed
```

The tests also mock external services where appropriate so core application behavior can be tested without depending on live Azure services.

---

# 🔐 Environment Variables

Create a local `.env` file:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE

TEST_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/TEST_DATABASE

AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH-SERVICE.search.windows.net
AZURE_SEARCH_INDEX_NAME=products
AZURE_SEARCH_API_KEY=YOUR_SEARCH_API_KEY

AZURE_OPENAI_ENDPOINT=https://YOUR-AZURE-OPENAI.openai.azure.com/
AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY
AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT
AZURE_OPENAI_API_VERSION=YOUR_API_VERSION
```

> **⚠️ Security:** Never commit real credentials, API keys, passwords, or other secrets to GitHub.

The repository uses:

```text
.env
```

in `.gitignore`.

A template is provided through:

```text
.env.example
```

---

# 🚀 Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/anvithayerneni/ai-ecommerce-shopping-assistant.git
cd ai-ecommerce-shopping-assistant
```

---

## 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the required database, Azure AI Search, and Azure OpenAI variables.

---

## 5. Run Database Migrations

```bash
alembic upgrade head
```

---

## 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 📖 API Documentation

FastAPI automatically provides interactive API documentation.

## Swagger UI

```text
http://127.0.0.1:8000/docs
```

## ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# 🐳 Docker

The project also includes Docker configuration.

## Build

```bash
docker build -t ai-ecommerce-shopping-assistant .
```

## Run

```bash
docker run -p 8000:8000 ai-ecommerce-shopping-assistant
```

The repository also contains:

```text
docker-compose.yml
```

for local multi-service development.

---

# ☁️ Deployment

The application is designed to be deployable as a **containerized FastAPI service**.

The production architecture can use:

```text
                Internet
                    │
                    ▼
              Render / Cloud
                    │
                    ▼
             FastAPI Service
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
     Neon DB   Azure Search   Azure OpenAI
```

---

# 📊 Example Catalog

The project currently works with a product catalog containing approximately:

```text
1,010 products
```

The catalog contains product information such as:

- Product ID
- Product name
- Brand
- Category
- Price
- Rating
- Tags
- Features
- Target audience
- Use cases

---

# 🧪 Evaluation

The project includes evaluation datasets for:

```text
data/recommendation_eval.json
data/retrieval_eval.json
```

Evaluation scripts are available under:

```text
scripts/
```

including:

```text
evaluate_recommendations.py
evaluate_retrieval.py
evaluate_category_classifier.py
```

This provides a foundation for measuring recommendation and retrieval quality rather than relying exclusively on subjective evaluation.

---

# 📈 Engineering Highlights

## 🤖 AI / ML

- Semantic vector search
- Text embeddings
- Recommendation ranking
- Natural-language query understanding
- Retrieval evaluation
- Recommendation evaluation
- Agentic LLM workflows

## ✨ Generative AI

- Azure OpenAI
- Tool calling
- Grounded generation
- Conversational follow-ups
- LangGraph state management

## ⚙️ Backend Engineering

- FastAPI
- REST API design
- PostgreSQL
- SQLAlchemy
- Alembic migrations
- Pydantic schemas
- Service-layer architecture
- Error handling
- Logging

## 🧑‍💻 Software Engineering

- Modular architecture
- Deterministic business logic
- Automated testing
- Mocked external dependencies
- Environment-based configuration
- Docker support
- Git/GitHub workflow

---

# 🔒 Security

Sensitive credentials are intentionally excluded from the repository.

The following are stored through environment variables:

```text
DATABASE_URL
TEST_DATABASE_URL
AZURE_SEARCH_ENDPOINT
AZURE_SEARCH_INDEX_NAME
AZURE_SEARCH_API_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_VERSION
```

The `.env` file is excluded using `.gitignore` to prevent sensitive credentials from being committed to the repository.

---

# 🧭 Future Improvements

Possible future extensions include:

- User authentication
- Persistent user profiles
- Long-term personalized recommendations
- Purchase history integration
- Product availability tracking
- Price-change monitoring
- Additional recommendation algorithms
- Hybrid collaborative + content-based recommendation
- Recommendation explainability dashboards
- Production observability
- Distributed caching
- Background recommendation jobs
- Larger product catalogs
- Automated evaluation pipelines
- CI/CD deployment workflows

---

# 📌 Project Scope

This project focuses on demonstrating an **end-to-end AI-powered shopping and recommendation architecture**.

It is not intended to function as a production e-commerce marketplace with:

- Payment processing
- Order fulfillment
- Inventory management
- Customer accounts
- Real-world checkout

Instead, the primary focus is on the **AI shopping and recommendation layer**, including product retrieval, filtering, ranking, comparison, grounded recommendations, agentic tool calling, and conversational interactions.

---

# 👩‍💻 Author

**Anvitha Yerneni**

AI / ML • Generative AI • Agentic AI • Python Backend

---

# 📜 License

This project is intended for educational and portfolio purposes.
