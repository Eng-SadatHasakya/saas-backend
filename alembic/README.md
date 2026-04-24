# 🚀 SaaS Backend API

A production-grade multi-tenant SaaS backend built with FastAPI, PostgreSQL, and Docker.

---

## 🔷 Overview

This backend powers a scalable SaaS platform with:

* Multi-tenant architecture (organization-based isolation)
* JWT authentication with refresh tokens
* Role-based access control (RBAC)
* Subscription management (Free, Pro, Enterprise)
* Token-based invite system
* API key authentication
* Full audit logging
* Database migrations using Alembic

---

## 🧱 Tech Stack

* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Authentication:** JWT (access + refresh tokens)
* **Migrations:** Alembic
* **Containerization:** Docker

---

## 📂 Project Structure

app/
├── models/
├── routers/
├── services/
├── auth/
├── core/
├── database.py
├── main.py

---

## 🔐 Authentication

* JWT-based authentication
* Access tokens (short-lived)
* Refresh tokens (long-lived)
* Role-based access per organization

---

## 🏢 Multi-Tenancy

* Each user belongs to an organization
* Strict tenant isolation enforced at query level
* No cross-tenant data access

---

## 📦 Features

### Users

* Create, update, delete users
* Role assignment (admin, member)

### Organizations

* Multi-tenant support
* Organization-level ownership

### Invitations

* Token-based invite system
* Secure onboarding flow

### Subscriptions

* Free / Pro / Enterprise plans
* Subscription tracking per organization

### API Keys

* `sk_` prefixed keys
* Alternative authentication mechanism

### Audit Logs

* Tracks critical system actions
* Security and compliance ready

---

## ⚙️ Environment Variables

Create a `.env` file:

DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```

---

## 🔄 Database Migrations

```bash
alembic upgrade head
```

---

## 🧪 API Documentation

Once running:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

---

## 🔑 Example Authentication Flow

1. Register/Login
2. Receive access + refresh token
3. Use access token for API calls
4. Refresh when expired

---

## 🚀 Deployment

Recommended platforms:

* AWS (EC2 / ECS)
* Render
* DigitalOcean
* Railway

---

## 📈 Future Improvements

* Payment integration (Stripe)
* Rate limiting
* Webhooks
* Microservices architecture

---

## 🧑‍💻 Author

Built by Pearl Tech Hub
