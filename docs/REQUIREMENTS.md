# LXP Requirements Specification

> Implementation-ready requirements document for an AI-native, xAPI-native, community-centric Learner Experience Platform (LXP).

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [High-Level System Requirements](#2-high-level-system-requirements)
3. [Domain Model Requirements](#3-domain-model-requirements)
4. [Data Storage Requirements](#4-data-storage-requirements)
5. [xAPI, cmi5, and LRS Requirements](#5-xapi-cmi5-and-lrs-requirements)
6. [AI-Native and RAG Requirements](#6-ai-native-and-rag-requirements)
7. [Frontend (Next.js/React) Requirements](#7-frontend-nextjsreact-requirements)
8. [Backend (Django/DRF) Requirements](#8-backend-djangodrf-requirements)
9. [Infrastructure and Deployment Requirements](#9-infrastructure-and-deployment-requirements)

---

## 1. Product Overview

The system is a **social, community-first learner experience platform (LXP)** where learning is organized around communities, conversations, and shared practice rather than just courses. It is:

- **AI-native**: Retrieval-augmented generation (RAG), LLM-based tutoring, and agentic workflows are core features.
- **xAPI-native**: All meaningful interactions emit xAPI statements into a strictly conformant LRS.
- **Interoperable**: Supports cmi5 packages for portable, LMS-compatible courseware when needed.
- **Analytics-driven**: In-app dashboards plus connections to external analytics/BI tools.

---

## 2. High-Level System Requirements

### 2.1 Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | **Next.js + React** SPA/SSR hybrid |
| Backend | **Python 3.x, Django + Django REST Framework (DRF)** |
| Transactional DB | **PostgreSQL** – users, communities, enrollments, assessments, etc. |
| Document DB | **MongoDB** – flexible content structures, drafts, AI artifacts |
| Vector Database | **Qdrant** (open source, self-hosted) |
| Object Storage | **MinIO** (S3-compatible, self-hosted) |
| Data Warehouse | **ClickHouse** (column-oriented analytics DB) |
| LRS | **SQL LRS (Yet Analytics)** or **Learning Locker (open-source)**, self-hosted and xAPI-conformant |
| OS/Hosting | **Ubuntu Server LTS** on VPS or bare metal; Docker/Compose for deployment |

### 2.2 Non-Functional Requirements

- Self-hostable on a single VPS/bare-metal node for initial deployments.
- Horizontally scalable service layout (stateless Django/Next.js pods, separate DBs).
- Secure-by-default:
  - TLS termination via reverse proxy.
  - Secrets via environment variables.
- Observability:
  - Centralized logging.
  - Basic metrics and health checks per service.

---

## 3. Domain Model Requirements

### 3.1 Users and Identity

The system shall support:

#### User Roles

- Learner
- Facilitator/instructor/catechist
- Admin
- (Optional) Parent/mentor

#### User Profiles

- Basic identity (name, email)
- Role(s)
- Optional metadata: interests, goals, communities, preferences

#### Passwordless Authentication

- Email-based magic links and/or one-time codes
- Optional social login (Google/Microsoft/Apple) via OIDC, pluggable later
- Backend issues JWT/OAuth tokens for frontend once identity is verified

### 3.2 Communities and Social Structures

The system shall support:

#### Communities

- Entities such as parish, cohort, ministry, class, interest group
- Community metadata: name, description, visibility, logo, tags
- Memberships with roles (member, facilitator, admin)

#### Groups / Small Circles

- Sub-communities for projects, study circles, mentoring
- Group membership and roles

#### Social Artifacts

- Threads (discussion topics)
- Posts and comments
- Reactions (like/upvote, etc.)
- Shared resources (links, files, content references)

Every social artifact shall be linked to:
- A community (required)
- Optionally: a specific learning activity or path

### 3.3 Learning Structures

The system shall support:

#### Activities

- **Types**: content viewing, discussion, reflection, assignment, quiz, project, peer activity
- **Metadata**: title, description, estimated time, outcomes, prerequisites, visibility
- Link to underlying content (stored in MongoDB or external cmi5 package)

#### Learning Paths

- Ordered or graph-like sequences of activities
- Multiple paths can be attached to a community
- Rules: prerequisites, branching conditions (basic in v1)

#### Assessments

- Items/questions, attempts, scores, feedback
- Mastery estimates at activity and outcome levels

---

## 4. Data Storage Requirements

### 4.1 PostgreSQL

Must store:

- Users, roles, auth records
- Communities, groups, memberships
- Activities, learning paths, paths-to-community mappings
- Enrollments and participation records
- Assessment definitions, attempts, scores
- Permissions and configuration

### 4.2 MongoDB

Must store:

- Content blocks (lesson bodies, rich JSON structures)
- AI-generated content variants (explanations, examples, feedback drafts)
- Draft states for activities and learning paths
- Optional: conversation metadata that benefits from flexible schemas

### 4.3 MinIO (Object Storage)

Must store:

- Media assets (video, audio, images)
- Documents (PDFs, DOCX, etc.)
- Packaged content (SCORM/cmi5 ZIPs)
- Exported reports/dashboards

### 4.4 ClickHouse (Data Warehouse)

Must store and serve:

- Ingested xAPI statements from LRS (mirrored/denormalized form)
- Platform event logs (non-xAPI internal events if needed)
- Aggregates for:
  - Participation and engagement
  - Social network metrics (contribution counts, reply patterns)
  - Learning outcomes (completion, mastery)
  - AI usage and agent actions

### 4.5 Qdrant (Vector Store)

Must store:

#### Embeddings

- Course content, transcripts, assessments
- Institutional/catechetical/policy documents
- Selected learner artifacts (notes, reflections, high-signal posts)

#### Metadata for Context-Aware Retrieval

- Community, activity, resource type
- Access control (visibility, roles)
- Language, timestamps

---

## 5. xAPI, cmi5, and LRS Requirements

### 5.1 xAPI Event Design

The platform shall:

#### Define an Internal xAPI Vocabulary

- Viewing content and activities
- Attempting and completing activities & assessments
- Social actions: posting, commenting, reacting, sharing, mentoring
- AI-mediated actions: requesting help, receiving AI feedback/explanations, agent interventions

#### Include Rich Context in Statements

- Community/group identifiers
- Activity/path identifiers
- Role (learner/facilitator)
- Device/client info where appropriate

#### Emission

**Backend (Django)** must emit xAPI for:
- Assessment results and mastery updates
- Enrollment changes and completions
- Agent decisions

**Frontend (Next.js)** must emit xAPI for:
- UI interactions and social actions that do not pass through a standard backend endpoint
- These events shall be forwarded securely to the LRS

### 5.2 LRS Integration

- The system shall integrate with a **strictly xAPI-conformant, open-source LRS**:
  - SQL LRS (Yet Analytics) or Learning Locker (open-source), initially
- LRS runs as a separate service and is the **canonical store** for xAPI statements
- The platform must:
  - Support authenticated HTTP xAPI calls to the LRS
  - Handle error and retry logic for LRS communication
- ClickHouse shall ingest/replicate xAPI data from the LRS via:
  - Batch ETL jobs and/or streaming, to be defined in ETL services

### 5.3 cmi5 Support (Interoperable Content)

The platform shall:

#### Support Importing cmi5 Packages

- Parse cmi5 XML
- Store package artifacts in MinIO
- Register activities/assignable units (AUs) linked to communities/paths

#### Implement cmi5 Launch

- Generate secure launch URLs and tokens
- Pass learner/context info according to cmi5 spec

#### Ensure

- AUs send xAPI statements to the chosen LRS
- The platform can correlate these statements (via context IDs) back to users, activities, and communities

---

## 6. AI-Native and RAG Requirements

### 6.1 LLM Integration

- The platform will use **LLM APIs** (e.g., OpenAI, Anthropic), not self-hosted models
- All LLM calls must go through internal **AI service abstractions**:
  - Services expose capabilities: `generate_explanation`, `generate_example`, `summarize_discussion`, `classify_response`, etc.
  - Underlying provider(s) must be swappable via configuration

### 6.2 RAG Pipeline

The system shall:

#### Provide a Pipeline to:

- Extract and chunk text from:
  - MongoDB content
  - Documents in MinIO (via text extraction workers)
  - Selected social artifacts and institutional documents
- Generate embeddings via an API-based embedding model
- Store embeddings and metadata in Qdrant

#### Provide a Retrieval Service that:

- Accepts queries with user, community, activity context
- Performs filtered vector search in Qdrant
- Returns documents with metadata for use in prompts and/or directly displayed citations

### 6.3 Agentic Workflows

The platform shall support:

#### Agents that:

- Monitor xAPI/warehouse data for patterns (e.g., low participation, misunderstandings)
- Propose or trigger actions:
  - Suggesting resources or activities to learners
  - Highlighting peer explanations or artifacts
  - Notifying facilitators of at-risk learners or hot discussion topics

#### Background Execution

- Agents run in background workers and:
  - Use platform APIs and warehouse queries to read state
  - Emit xAPI statements for their own actions for traceability

### 6.4 Governance and Provenance

- Every AI interaction must be **logged**:
  - Inputs (abstracted/sanitized where necessary)
  - Outputs
  - Sources used (RAG documents)
  - Decision metadata (which agent, which policy)
- The learner and facilitator UIs must:
  - Show **provenance**: which documents or posts informed an AI answer
  - Allow users to see/expand source snippets

---

## 7. Frontend (Next.js/React) Requirements

### 7.1 Core Interfaces

The frontend shall provide:

#### Community Home

- Activity feed (posts, new activities, milestones)
- Recommended activities and resources
- AI-generated summaries of what's happening

#### Activity View

- Main learning task content
- Embedded discussion thread and shared artifacts
- Contextual AI assistant (help, explanations, examples)

#### Group/Small-Circle Pages

- Dedicated spaces for group projects and study circles

#### Facilitator Dashboards

- Cohort and community summaries
- Key metrics (engagement, participation, mastery)
- AI-generated overviews and suggested interventions

### 7.2 Auth and Session Handling

- Implement passwordless login:
  - Email magic link / code request
  - Link redirects to Next.js, which exchanges token with Django for session/JWT
- Support social login (configurable) with minimal friction

---

## 8. Backend (Django/DRF) Requirements

### 8.1 Django Apps

At minimum:

| App | Purpose |
|-----|---------|
| `accounts` | Users, roles, passwordless auth, tokens, (future) SSO |
| `communities` | Communities, groups, memberships |
| `content` | Activities, learning paths, content references (MongoDB/MinIO pointers) |
| `social` | Threads, posts, comments, reactions |
| `assessments` | Items, attempts, scoring, mastery |
| `xapi_integration` | xAPI vocab, statement builders, LRS configuration, cmi5 |
| `ai_services` | Wrappers for LLM/RAG and agents |
| `analytics` | ClickHouse integration and metrics APIs |

### 8.2 API Design

#### RESTful APIs via DRF

- CRUD on communities, groups, activities, paths, assessments, social artifacts
- Auth/session management and login flows
- Analytics endpoints for dashboards

#### Internal Utility Modules

- Emitting xAPI statements
- Dispatching AI service calls
- Scheduling background tasks

### 8.3 Background Jobs

Use Celery/RQ (or similar) for:

- ETL from LRS to ClickHouse
- Embedding generation and Qdrant updates
- Long-running agent workflows
- cmi5 imports and preprocessing

---

## 9. Infrastructure and Deployment Requirements

### 9.1 Dockerized Services

| Service | Description |
|---------|-------------|
| Django API | Main backend application |
| Next.js Frontend | Client-facing web application |
| PostgreSQL | Relational database |
| MongoDB | Document database |
| Qdrant | Vector database |
| MinIO | Object storage |
| ClickHouse | Analytics warehouse |
| LRS | SQL LRS or Learning Locker |
| Background Worker(s) | Celery/RQ workers |
| Reverse Proxy | Nginx/Traefik |

### 9.2 Environments

- **Local Development**: Docker Compose
- **Staging/Production**: Environment-specific configuration

### 9.3 Analytics Integration

- Provide read-only connections (or API endpoints) for external BI tools to access ClickHouse (and optionally Postgres)

---

## Document History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | December 2024 | Initial requirements specification |

---

## License

This documentation is part of the LXP project and is licensed under the GNU General Public License v3.0.
