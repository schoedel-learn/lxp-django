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

- **Frontend**: Next.js + React
- **Backend**: Python 3.x, Django + Django REST Framework
- **Databases**: PostgreSQL, MongoDB, Qdrant, ClickHouse
- **Storage**: MinIO (S3-compatible)
- **LRS**: SQL LRS (Yet Analytics) or Learning Locker

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
