# Here is the AIFacade-specific documentation related to this Python web application

1. The complete Marketing requirements document.
[Marketing Requirements Document](docs/marketing_requirements_document.md)

2. The Software Specification Document.
[Software Specification Document](docs/software_specification_document.md)

3. The Analysis and Design document. Associated UML diagrams are referenced in the ADD document.
[Analysis and Design Document](docs/analysis_and_design_document.md)

4. The last successful testing report.
[Last Test Report Local](docs/tests/htmlcov/)

5. The Deployment Document. The CI/CD document should be included.
[Deployment and CI/CD Document](docs/deployment_and_ci_cd_document.md)

6. The maintenance document.
[Maintenance Document](docs/maintenance_document.md)

The complete production-ready setup with Docker, Gunicorn, and pytest integration, building on the previous enhancements:

**1. Docker Setup**
_Dockerfile (Root of your project)_

-Base image
FROM python:3.9-slim

-Set working directory
WORKDIR /app

-Install system dependencies (required for SQLite and others)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

-Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

-Copy the entire project
COPY . .

-Environment variables (override with `docker run --env-file .env`)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

-Run Gunicorn (WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

_docker-compose.yml (For multi-container setup)_

version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env  # Load API keys and secrets
    volumes:
      - .:/app  # Hot-reload for development (remove in production)
      
**2. Gunicorn Configuration**
_gunicorn.conf.py (Optimized for production)_
workers = 4  # Number of worker processes
bind = "0.0.0.0:5000"
timeout = 120  # For async requests
keepalive = 5
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr

**3. Pytest Setup**
_tests/ Directory Structure_

tests/
├── conftest.py      # Fixtures
├── test_auth.py     # Auth tests
├── test_chat.py     # API tests
└── test_errors.py   # Error handling

_conftest.py (Shared fixtures)_

import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app(config_class="config.TestConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
    
_Example Test: test_chat.py_

import pytest
from app.models import User

def test_chat_endpoint(client):
    # Login (mocked)
    user = User(username="test", password="test")
    db.session.add(user)
    db.session.commit()

    # Send a prompt
    response = client.post("/chat", data={"prompt": "Hello"}, follow_redirects=True)
    assert b"DeepSeek" in response.data
    
_Run Tests_
bash
pytest tests/ -v  # Verbose mode

**4. Production Deployment**
_Deploy with Docker_
bash
docker build -t deepseek-app .
docker run -d --env-file .env -p 5000:5000 deepseek-app
_Or with Docker Compose_
bash
docker-compose up --build -d

**5. Key Files Recap**
1. Dockerfile – Container setup.
2. docker-compose.yml – Multi-service orchestration.
3. gunicorn.conf.py – Production WSGI server.
4. tests/ – Pytest integration.

**6. CI/CD (GitHub Actions)**
_.github/workflows/deploy.yml_

name: Deploy
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: docker-compose up -d --build
      - run: pytest tests/
      
Final Notes
✅ Docker – Isolated, reproducible environments.
✅ Gunicorn – Scalable production server.
✅ Pytest – Reliable testing.
✅ CI/CD Ready – Automated deployments.


