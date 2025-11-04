# FastAPI Project

![CI](https://github.com/edi2410/algebra-radegast/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/edi2410/algebra-radegast/branch/main/graph/badge.svg)](https://codecov.io/gh/edi2410/algebra-radegast)
[View test coverage](https://<tvoj-korisnik>.github.io/<repo>/index.html)


## Setup Instructions

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure `.env` file
6. Run migrations: `alembic upgrade head`
7. Start server: `uvicorn app.main:app --reload`

## Docker Deployment

```bash
docker-compose up --build
```

## API Documentation 

Swagger UI:
http://localhost:8000/api/docs

ReDoc:
http://localhost:8000/api/redoc

edited by programmer 1

---

## 🚀 **Pokretanje kompletnog projekta**

```bash
# 1. Clone
git clone <repo>
cd project

# 2. Run docker
docker-compose up --build

# 3. App access
# API: http://localhost:8000
# Docs: http://localhost:8000/api/docs
# Health: http://localhost:8000/health
