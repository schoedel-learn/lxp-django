# LXP Technology Stack Overview

> A comprehensive guide to the technologies, languages, dependencies, and architecture of the Learner Experience Platform (LXP).

---

## Table of Contents

1. [Languages](#1-languages)
2. [Framework & Core Libraries](#2-framework--core-libraries)
3. [Databases & Data Stores](#3-databases--data-stores)
4. [Infrastructure Services](#4-infrastructure-services)
5. [AI & Machine Learning](#5-ai--machine-learning)
6. [Learning Standards](#6-learning-standards)
7. [Python Dependencies](#7-python-dependencies)
8. [Development Tools](#8-development-tools)
9. [Architecture Overview](#9-architecture-overview)
10. [Service Ports Reference](#10-service-ports-reference)

---

## 1. Languages

| Language | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.12+ | Backend API, business logic, data processing |
| **SQL** | - | PostgreSQL queries, ClickHouse analytics |
| **JavaScript/TypeScript** | - | Frontend (Next.js - separate repository) |

---

## 2. Framework & Core Libraries

### Backend Framework

| Package | Version | Purpose |
|---------|---------|---------|
| **Django** | 5.1.4+ | Web framework, ORM, admin interface |
| **Django REST Framework** | 3.14+ | RESTful API development |
| **django-cors-headers** | 4.3+ | Cross-Origin Resource Sharing support |
| **django-filter** | 24.0+ | API filtering and search |

### Why Django?
- **Batteries included**: Built-in admin, ORM, authentication, migrations
- **Mature ecosystem**: Extensive packages for learning platforms
- **Security**: Built-in protection against common vulnerabilities
- **Scalability**: Proven at scale (Instagram, Pinterest, Disqus)

---

## 3. Databases & Data Stores

### Primary Databases

| Database | Version | Purpose | Port |
|----------|---------|---------|------|
| **PostgreSQL** | 16 | Transactional data (users, communities, enrollments) | 5432 |
| **MongoDB** | 7.0 | Document storage (content blocks, AI artifacts) | 27017 |

### Specialized Data Stores

| Service | Version | Purpose | Port |
|---------|---------|---------|------|
| **Redis** | 7 | Caching, Celery message broker | 6379 |
| **ClickHouse** | Latest | Analytics warehouse, xAPI statement aggregation | 8123, 9009 |
| **Qdrant** | Latest | Vector database for RAG embeddings | 6333, 6334 |
| **MinIO** | Latest | S3-compatible object storage (media, cmi5 packages) | 9000, 9001 |

### Database Drivers

| Package | Purpose |
|---------|---------|
| **psycopg[binary]** | PostgreSQL adapter (async-capable) |
| **djongo** | MongoDB integration with Django ORM |
| **pymongo** | Direct MongoDB client |
| **redis** | Redis client for Python |
| **clickhouse-connect** | ClickHouse HTTP client |
| **qdrant-client** | Qdrant vector database client |

---

## 4. Infrastructure Services

### Container Platform

| Technology | Purpose |
|------------|---------|
| **Docker** | Application containerization |
| **Docker Compose** | Multi-container orchestration |

### Application Servers

| Service | Purpose |
|---------|---------|
| **Gunicorn** | WSGI HTTP server for production |
| **WhiteNoise** | Static file serving |

### Task Processing

| Package | Version | Purpose |
|---------|---------|---------|
| **Celery** | 5.3+ | Distributed task queue |
| **Celery Beat** | - | Scheduled task runner |
| **Redis** | 5.0+ | Message broker for Celery |

### Task Queue Use Cases
- ETL jobs from LRS to ClickHouse
- Embedding generation for RAG pipeline
- AI agent background workflows
- cmi5 package processing
- Report generation

### Storage

| Package | Purpose |
|---------|---------|
| **boto3** | AWS S3/MinIO SDK |
| **django-storages** | Django storage backend abstraction |

---

## 5. AI & Machine Learning

### LLM Integration

| Package | Version | Purpose |
|---------|---------|---------|
| **openai** | 1.12+ | OpenAI API client (GPT-4, embeddings) |
| **tiktoken** | 0.6+ | Token counting for OpenAI models |

### RAG (Retrieval-Augmented Generation) Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Content   │────▶│  Embeddings │────▶│   Qdrant    │
│  (MongoDB)  │     │  (OpenAI)   │     │  (Vectors)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Response  │◀────│    LLM      │◀────│   Context   │
│  to Learner │     │  (GPT-4)    │     │  Retrieval  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### AI Capabilities
- `generate_explanation` - Explain concepts
- `generate_example` - Create examples
- `summarize_discussion` - Summarize threads
- `classify_response` - Assess learner responses
- `generate_feedback` - Provide AI feedback
- `answer_question` - Contextual Q&A

---

## 6. Learning Standards

### xAPI (Experience API)

| Component | Purpose |
|-----------|---------|
| **xAPI Statements** | Learning activity records |
| **LRS Integration** | Statement storage and retrieval |
| **Custom Vocabulary** | Platform-specific verbs and activity types |

### cmi5

| Feature | Purpose |
|---------|---------|
| **Package Import** | Parse cmi5.xml, extract AUs |
| **Launch Protocol** | Secure content launching |
| **Session Tracking** | Track learner progress in AUs |

### Supported LRS Options
- **SQL LRS** (Yet Analytics) - Recommended
- **Learning Locker** - Open source alternative

---

## 7. Python Dependencies

### Complete Package List

```txt
# Django Core
Django>=5.1.4,<6.1           # Web framework
djangorestframework>=3.14    # REST API
django-cors-headers>=4.3     # CORS support
django-filter>=24.0          # API filtering

# Database Drivers
psycopg[binary]>=3.1         # PostgreSQL
djongo>=1.3                  # MongoDB ODM
pymongo>=4.6                 # MongoDB client

# Authentication
PyJWT>=2.8                   # JSON Web Tokens
django-sesame>=3.2           # Magic link authentication

# Task Queue
celery>=5.3                  # Async task queue
redis>=5.0                   # Redis client

# Storage
boto3>=1.34                  # S3/MinIO SDK
django-storages>=1.14        # Storage backends

# Vector Database
qdrant-client>=1.7           # Qdrant client

# Analytics
clickhouse-connect>=0.7      # ClickHouse client

# AI/LLM
openai>=1.12                 # OpenAI API
tiktoken>=0.6                # Token counting

# Utilities
python-decouple>=3.8         # Environment config
gunicorn>=21.2               # WSGI server
whitenoise>=6.6              # Static files

# Development
pytest>=8.0                  # Testing framework
pytest-django>=4.8           # Django test integration
```

---

## 8. Development Tools

### Testing

| Tool | Purpose |
|------|---------|
| **pytest** | Test runner |
| **pytest-django** | Django integration |

### Configuration

| Tool | Purpose |
|------|---------|
| **python-decouple** | Environment variable management |

### Running the Project

```bash
# Development with Docker
docker-compose up -d

# Local development (SQLite)
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest
```

---

## 9. Architecture Overview

### System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         Frontend                                │
│                    (Next.js + React)                           │
└────────────────────────────┬───────────────────────────────────┘
                             │ REST API
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      Django API                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ accounts │ │communities│ │ content  │ │  social  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │assessments│ │   xapi   │ │ai_services│ │analytics │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└────────────────────────────┬───────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ PostgreSQL  │     │   MongoDB   │     │    Redis    │
│(Transactional)    │ (Documents) │     │  (Cache)    │
└─────────────┘     └─────────────┘     └─────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ ClickHouse  │     │   Qdrant    │     │   MinIO     │
│ (Analytics) │     │ (Vectors)   │     │  (Storage)  │
└─────────────┘     └─────────────┘     └─────────────┘
         │
         ▼
┌─────────────┐
│     LRS     │
│   (xAPI)    │
└─────────────┘
```

### Django App Structure

| App | Models | Purpose |
|-----|--------|---------|
| **accounts** | User, UserRoleAssignment, MagicLink, RefreshToken | Authentication & authorization |
| **communities** | Community, Group, CommunityMembership, GroupMembership | Social structures |
| **content** | Activity, LearningPath, PathActivity, Enrollment, ActivityProgress | Learning content |
| **social** | Thread, Post, Comment, Reaction, SharedResource | Social features |
| **assessments** | Assessment, Question, Choice, AssessmentAttempt, QuestionResponse, MasteryEstimate | Quizzes & mastery |
| **xapi_integration** | LRSConfiguration, XAPIVerb, CMI5Package, CMI5Session, StatementQueue | Learning standards |
| **ai_services** | AIProvider, AICapability, EmbeddingCollection, AIAgent, AIInteraction | AI features |
| **analytics** | AnalyticsConnection, MetricDefinition, Dashboard, DashboardWidget, ETLJob | Reporting |

---

## 10. Service Ports Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Django API | 8000 | HTTP | REST API |
| PostgreSQL | 5432 | TCP | Database |
| MongoDB | 27017 | TCP | Document DB |
| Redis | 6379 | TCP | Cache/Queue |
| MinIO API | 9000 | HTTP | Object storage |
| MinIO Console | 9001 | HTTP | Admin UI |
| Qdrant HTTP | 6333 | HTTP | Vector API |
| Qdrant gRPC | 6334 | gRPC | Vector API |
| ClickHouse HTTP | 8123 | HTTP | Analytics API |
| ClickHouse Native | 9009 | TCP | Native protocol |

---

## Quick Reference Card

### Key Technologies at a Glance

| Category | Technology |
|----------|------------|
| **Language** | Python 3.12 |
| **Framework** | Django 5.1 + DRF |
| **Primary DB** | PostgreSQL 16 |
| **Document DB** | MongoDB 7.0 |
| **Cache/Queue** | Redis 7 |
| **Vector DB** | Qdrant |
| **Analytics** | ClickHouse |
| **Object Storage** | MinIO |
| **Task Queue** | Celery |
| **AI Provider** | OpenAI (GPT-4) |
| **Learning Standards** | xAPI, cmi5 |
| **Containers** | Docker + Compose |

---

## License

This documentation is part of the LXP project and is licensed under the GNU General Public License v3.0.
