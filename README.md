# 🚀 AI-Powered Multi-Tenant SaaS Platform

A production-grade, real-time, AI-enabled SaaS backend built with FastAPI, PostgreSQL, Redis, and WebSockets.

![CI Pipeline](https://github.com/Eng-SadatHasakya/saas-backend/actions/workflows/ci.yml/badge.svg)

## 🏗️ Architecture
┌─────────────────────────────────────────────┐
│                API Gateway :8080             │
└──────────────────┬──────────────────────────┘
│
┌──────────────┼──────────────┐
│              │              │
┌───▼───┐    ┌────▼────┐   ┌────▼────┐
│ Auth  │    │   AI    │   │Notif.   │
│ :8001 │    │  :8003  │   │  :8002  │
└───────┘    └─────────┘   └─────────┘
│
┌──────────────────▼──────────────────────────┐
│              Main API :8000                  │
│  FastAPI + SQLAlchemy + Redis + WebSocket    │
└──────────────────┬──────────────────────────┘
│
┌─────────▼─────────┐
│    PostgreSQL      │
│    Redis Cache     │
└───────────────────┘

## ✨ Features

- 🔐 **JWT Authentication** — Access + refresh tokens with revocation
- 👥 **Multi-Tenancy** — Complete organization data isolation
- 🤖 **AI Assistant** — Groq LLaMA powered, tenant-aware
- ⚡ **Real-Time** — WebSocket with live notifications
- 💳 **Payments** — Stripe checkout and subscription management
- 📧 **Invite System** — Token-based team onboarding
- 🔑 **API Keys** — sk_ prefixed with expiry management
- 🚀 **Microservices** — Auth, AI, Notification services
- 📊 **Monitoring** — Redis cache stats, DB optimization
- 🔄 **CI/CD** — GitHub Actions with automated testing

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python 3.13) |
| Database | PostgreSQL 18 |
| Cache | Redis |
| ORM | SQLAlchemy + Alembic |
| Auth | JWT + python-jose |
| AI | Groq LLaMA 3.3 70B |
| Payments | Stripe |
| Real-Time | WebSockets |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## 📡 API Endpoints

### Auth
| Method | Endpoint | Access |
|--------|----------|--------|
| POST | /auth/register | Public |
| POST | /auth/login | Public |
| POST | /auth/refresh | Authenticated |
| POST | /auth/logout | Authenticated |

### Users
| Method | Endpoint | Access |
|--------|----------|--------|
| GET | /users/ | Admin |
| GET | /users/me | Authenticated |
| POST | /users/ | Admin |
| DELETE | /users/{id} | Admin |

### AI
| Method | Endpoint | Access |
|--------|----------|--------|
| POST | /ai/query | Authenticated |

### Billing
| Method | Endpoint | Access |
|--------|----------|--------|
| GET | /billing/info | Authenticated |
| POST | /billing/checkout/{plan} | Admin |

## 🚀 Quick Start

### Local Development
```bash
# Clone
git clone https://github.com/Eng-SadatHasakya/saas-backend.git
cd saas-backend

# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your values

# Database
alembic upgrade head

# Run
uvicorn app.main:app --reload
```

### Docker
```bash
docker-compose up --build
```

## 🧪 Testing
```bash
pytest tests/ -v
```

## 📁 Project Structure

app/
├── core/          # Centralized config, security, cache
├── models/        # Database models
├── routes/        # API endpoints
├── services/      # Business logic
├── websocket/     # WebSocket manager
└── ai/            # AI prompts and service
services/
├── auth-service/        # Standalone auth microservice
├── ai-service/          # Standalone AI microservice
├── notification-service/ # Standalone notification microservice
└── api-gateway/         # API gateway

## 👤 Author

**Eng. Sadat Hasakya**
- GitHub: [@Eng-SadatHasakya](https://github.com/Eng-SadatHasakya)
- Email: hersacemusasadat@gmail.com

## 📄 License

MIT
