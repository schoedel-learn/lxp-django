# lxp-django

Learner Experience Platform (LXP) - A social, community-first learning platform that is AI-native, xAPI-native, and analytics-driven.

## Overview

This project is a comprehensive Learner Experience Platform where learning is organized around communities, conversations, and shared practice rather than just courses.

### Key Features

- **AI-Native**: Retrieval-augmented generation (RAG), LLM-based tutoring, and agentic workflows
- **xAPI-Native**: All meaningful interactions emit xAPI statements into a conformant LRS
- **Interoperable**: Supports cmi5 packages for portable, LMS-compatible courseware
- **Analytics-Driven**: In-app dashboards plus connections to external analytics/BI tools

## Documentation

- [Requirements Specification](docs/REQUIREMENTS.md) - Complete implementation-ready requirements document

## Technology Stack

- **Frontend**: Next.js + React (separate repository)
- **Backend**: Python 3.12+, Django 5.0+, Django REST Framework
- **Databases**: 
  - PostgreSQL (transactional data)
  - MongoDB (content and AI artifacts)
  - Qdrant (vector embeddings)
  - ClickHouse (analytics warehouse)
- **Storage**: MinIO (S3-compatible)
- **LRS**: SQL LRS (Yet Analytics) or Learning Locker
- **Task Queue**: Celery with Redis

## Project Structure

```
lxp-django/
├── lxp_core/           # Django project settings
├── accounts/           # User management, auth, roles
├── communities/        # Communities, groups, memberships
├── content/            # Activities, learning paths, enrollments
├── social/             # Threads, posts, comments, reactions
├── assessments/        # Quizzes, questions, attempts, mastery
├── xapi_integration/   # xAPI/cmi5 integration with LRS
├── ai_services/        # LLM/RAG integration, agents
├── analytics/          # ClickHouse integration, dashboards
├── docs/               # Documentation
├── docker-compose.yml  # Development environment
├── Dockerfile          # Container configuration
└── requirements.txt    # Python dependencies
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/lxp-django.git
   cd lxp-django
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Run migrations:
   ```bash
   docker-compose exec api python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec api python manage.py createsuperuser
   ```

6. Access the services:
   - Django API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - MinIO Console: http://localhost:9001
   - ClickHouse: http://localhost:8123

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy and configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your local database settings
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Django Apps

| App | Description |
|-----|-------------|
| `accounts` | Custom user model, roles, passwordless auth, JWT tokens |
| `communities` | Communities, groups, memberships |
| `content` | Activities, learning paths, enrollments, progress tracking |
| `social` | Threads, posts, comments, reactions, shared resources |
| `assessments` | Questions, assessments, attempts, scoring, mastery |
| `xapi_integration` | xAPI vocabulary, LRS config, cmi5 packages |
| `ai_services` | LLM providers, RAG pipeline, agents, interaction logging |
| `analytics` | ClickHouse connection, metrics, dashboards, reports |

## API Endpoints

All API endpoints are prefixed with `/api/v1/`:

- `/api/v1/accounts/` - Authentication and user management
- `/api/v1/communities/` - Community and group management
- `/api/v1/content/` - Activities, paths, enrollments
- `/api/v1/social/` - Social features (threads, posts, etc.)
- `/api/v1/assessments/` - Assessment management
- `/api/v1/xapi/` - xAPI and cmi5 integration
- `/api/v1/ai/` - AI service endpoints
- `/api/v1/analytics/` - Analytics and reporting

## Environment Variables

See [.env.example](.env.example) for all available configuration options.

Key variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (False in production)
- `DB_*` - PostgreSQL connection settings
- `MONGODB_*` - MongoDB connection settings
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `LRS_*` - Learning Record Store configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python manage.py test`
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
