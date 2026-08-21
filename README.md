# AI-Powered E-Commerce Shopping & Recommendation Assistant

Badges

## Overview
## Key Features
## Example Queries
## Architecture
## Technical Design
## Project Structure
## Tech Stack
## API
## Setup
## Environment Variables
## Running the Application
## Testing
## Example Responses
## Engineering Highlights
## Roadmap
## License

## 🚀 Project Status

**Status:** Active Development

The core shopping recommendation pipeline is implemented and
covered by automated tests.

### Implemented

- FastAPI backend
- PostgreSQL product catalog
- Product search and retrieval
- Azure AI Search vector search
- Embedding-based semantic search
- Deterministic product filtering
- Product reranking
- Natural-language query understanding
- LangGraph shopping workflow
- Azure OpenAI integration
- Tool-calling shopping agent
- Product comparison
- Product-name resolution
- Conversational follow-up handling
- Grounded response generation
- Product attribute grounding
- Automated test suite
- 118 passing tests

  ## ✨ Key Features

### 🔎 Natural-Language Product Search

Users can search for products using natural language rather than
traditional keyword filters.

Examples:

- "laptop under $1000 for programming"
- "running shoes for training"
- "headphones with good ratings"

The system extracts structured constraints such as:

- category
- use case
- minimum price
- maximum price
- minimum rating

---

### 🧠 Semantic Product Search

Product queries are converted into embeddings and searched using
Azure AI Search vector search.

This allows the system to retrieve products based on semantic
similarity rather than relying only on exact keyword matches.

---

### 🎯 Deterministic Filtering

Structured constraints are enforced in Python rather than relying
entirely on the LLM.

Supported filters include:

- Category
- Minimum price
- Maximum price
- Minimum rating
- Use case

---

### 📊 Product Reranking

Retrieved products are reranked using product relevance signals
before recommendations are generated.

---

### 🤖 Agentic Tool Calling

The shopping agent can use product tools to retrieve authoritative
catalog information.

The system supports tool-based product retrieval and comparison
rather than allowing the LLM to invent product attributes.

---

### ⚖️ Product Comparison

Users can compare products using natural language.

Example:

"Compare MacBook Air M3 and Galaxy Book4"

The comparison can identify:

- Product names
- Brands
- Categories
- Prices
- Ratings
- Features
- Target audience
- Use cases
- Cheapest product
- Highest-rated product

---

### 🛡️ Grounded Responses

The assistant is designed to avoid hallucinating product
capabilities.

Product features and use cases must come from retrieved catalog
data.

For example, if programming is explicitly listed for one product
but not another, the system does not automatically assume that both
support programming.

---

### 💬 Conversational Follow-Ups

The system maintains short-term conversation state and can resolve
follow-up requests such as:

- "Show me cheaper ones"
- "Show me more expensive ones"
- "Show me Windows ones"

                           User
                           |
                           v
                    FastAPI API
                           |
                           v
                Shopping Assistant
                           |
                           v
                  Query Understanding
                           |
                           v
                  Resolve Follow-Up
                           |
                           v
                   LangGraph Workflow
                           |
              +------------+-------------+
              |                          |
              v                          v
       Shopping Agent              Product Search
              |                          |
              v                          v
        Tool Calling              Azure AI Search
              |                          |
              v                          v
      PostgreSQL Catalog          Vector Embeddings
              |                          |
              +------------+-------------+
                           |
                           v
                  Deterministic Filters
                           |
                           v
                       Reranking
                           |
                           v
                    Recommendations
                           |
                           v
                 Grounding Validation
                           |
                           v
                    Azure OpenAI
                           |
                           v
                  Final Response

## 🔌 API

### Product Recommendations

```http
GET /assistant/recommend

## 🏗️ Engineering Highlights

### Separation of Deterministic and Generative Logic

The system intentionally separates deterministic business logic
from LLM-generated responses.

Structured constraints such as price, category, rating, and use case
are processed programmatically.

The LLM is primarily responsible for conversational interpretation
and response generation.

### Grounded Product Comparisons

Product comparisons are generated from authoritative catalog data.

The system does not allow the LLM to invent:

- prices
- ratings
- features
- use cases
- product capabilities

### Stateful Conversational Workflow

LangGraph manages the shopping workflow and short-term conversation
state, allowing follow-up requests to reference previous
recommendations.

### Lazy Azure OpenAI Initialization

Azure OpenAI clients are created lazily so the application can be
imported and tested without requiring Azure credentials during
module import.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Azure AI Search
- Azure OpenAI
- Git

### Clone

```bash
git clone https://github.com/anvithayerneni/ai-ecommerce-shopping-assistant.git
cd ai-ecommerce-shopping-assistant


  
