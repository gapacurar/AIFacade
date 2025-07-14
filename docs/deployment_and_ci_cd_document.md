# Deployment and CI/CD Document

## 1. Overview

This document describes the steps and technologies used to deploy and manage the AIFacade application across environments. It includes local Docker usage, container orchestration and continuous integration/deployment via GitHub Actions.

## 2. Deployment Architecture

User → Caddy (TLS termination) → Gunicorn (WSGI HTTP server) → Flask App (via Factory Pattern)
                                                 ↓
                                         SQLite (Local DB)

__Web server__: Caddy handles HTTPS (self-signed for dev).
__App server__: Gunicorn runs Flask inside Docker container.
__DB__: SQLite stored persistently via instance/ volume.

**TO DO**
**A components/deployment diagram should be creted here to understand the interconections and the platform. The docker component should be represented here also. The role of port 5000 should be also visible.**

## 3. Local Deployment (Developer Environment)

To run the app locally with Docker:

```bash
docker compose build
docker compose up

```

This app is accessible at: __<https://localhost>__

To shut down:

```bash
docker compose down --volumes
```

Volumes:
    -./instance:/app/instance ensures the SQLite DB persists across restarts.
    - caddy_data and caddy_config persist TLS certs.

Note: Although Gunicorn runs on port 5000 ---the standard port used by Flask app in development---, you're not connecting to it directly. The Caddyfile proxies HTTPS requests on port 443 (the default for browsers) to Gunicorn at web:5000. This allows you to simply use __<https://localhost>__ in your browser.

## 4. Dockerfile

The *Dockerfile* builds a slim Python 3.13.5 image, installing only the necessary system and Python dependencies. Notable elements:
    - Uses pip install --no-cache-dir -r requirements.txt
    - Runs Gunicorn with config: CMD ["gunicorn", "--config", "gunicorn.conf.py", "project:create_app()"]

## 5. Gunicorn Configuration

*gunicorn.conf.py*:

```python
bind = "0.0.0.0:5000"
workers = 4
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
```

This config starts with 4 workers, waits up to 120 seconds before killing a request and Logs to stdout/stderr

The timeout = 120 setting tells Gunicorn to wait up to 120 seconds for a worker to complete a request before forcefully terminating it.
This is important for handling long-running requests—such as calls to external APIs, AI model inference, or chat generation—that may take longer than the default timeout (30 seconds).
Without this increased timeout, Gunicorn could prematurely kill valid but slow requests, leading to user-facing errors.

## 6. Cady Configuration

```c
localhost {
    reverse_proxy web:5000
    tls internal
}
```

Accept requests on __localhost__, it secures them with a self-signed TLS cert and forwards the traffic to a backend services running at web:5000.
This is suitable for test/dev environments only.

## 7. Environment Variables

Stored via .env file and loaded into the container:
    - __DEEPSEEK_API_KEY__
    - __SECRET_KEY__

## 8. GitHub Actions (CI/CD)

File: .github/workflows/deploy.yml

### Trigger

Push to main or final-exam

### Steps

Checkout Code

Set up Docker BuildX

Build Containers (docker compose build)

Start App in Background (docker compose up -d)

Wait 5 seconds (optional init wait)

Run Tests (docker compose run --rm web pytest tests/ -v)

Tear Down (docker compose down --volumes)

**TO DO**
**When you specify a mandatory irder of the list please use a numbered list. I mean from 1 to 7 in our case.**

### Notes

Tests run in a temporary container with the app context.

Secrets (like the API key) must be provided in repository/environment settings.

**TO DO**
**Please elaborate more these two sentences. These are too abstract.**

## 9. Assumptions & Requirements

Docker, Docker Compose, and GitHub Actions must be installed/configured.
TLS termination is handled by Caddy using internal self-signed certificates.
SQLite used only for v1. Migration needed for production readiness.
No staging/production environments defined yet.

## 10. Future Enhancements

1. Add support for PostgreSQL or MySQL via Docker.
2. Add staging deployment branch.
3. Implement GitHub environments or runners for deployment approvals.
4. Use Docker secrets or HashiCorp Vault for managing credentials.
5. Add rollback support in case of test failure or bad deploy.

**TO DO**
**Here please specify also the extended flexibility for the user to chose another AI engine**.
