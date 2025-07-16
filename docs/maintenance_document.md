# Maintenance Document

## Document Control

**TO DO** Please update the status of Document Control (date).

- **Version:** 1.0
- **Date:** 2025-06-30
- **Authors:** Bicu Andrei Ovidiu
- **Status:** Final


## Overview

This document provides guidelines for maintaining the Flask web application deployed via Docker, Gunicorn, and Caddy. It includes instructions for updates, logging, monitoring, dependency management,t and common troubleshooting procedures.

## 1. Application Updates

### Code Updates

- All changes must be pushed to the __main__ or __final-exam__ branches.
- GitHub Actions (__.github/workflows/deploy.yml__) automatically:
                    - Builds the Docker containers.
                    - Runs tests
                    - Deploys the updated containers

### Dependency Updates

- Use __pip list --outdated__ inside the container to check out outdated packages.
- Update __requirements.txt__:

```bash
pip install --upgrade <package>
pip freeze > requirements.txt
```

Rebuild the containers:

```bash
docker compose build
docker compose up -d
```

Or you can rebuild and run the container with:

```bash
docker compose up --build -d
```

## 2. Logs and Debugging

### Gunicorn Logs

- Output is shown in the container logs.
View logs:

```bash
docker logs flask_app
```

## Caddy Logs

Caddy logs HTTP requests and TLS status.

```bash
docker logs caddy
```

### GitHub Actions Logs

Navigate to your repo -> "Actions" tab -> Select latest run -> Check step-by-step logs.

## 3. Monitoring and Health

### Manual Health Checks

Test app with:

With self-signed certs.

```powershell
curl.exe -k https://localhost
```

With real TLS

```powershell
curl https://localhost
```

*Update the URL provided as needed.

Or browser: __<https://localhost>__

### Optional Enhancements

Add monitoring like __Prometheus__, __Grafana__ or Flask extensions (e.g., __Flask-Healthz__)

## 4. Cleaning and Recovery

Stopping and Cleaning Up

```bash
docker compose down --volumes
```

Reset SQLite (dev only)

```bash
rm -rf ./instance/*
```

## 5. Testing in development

1. Trigger a GitHub workflow manually (via UI or pushing a test branch)
2. Use

```bash
docker compose run --rm web pytest tests/ -v
```

## 6. Security Maintenance

Monitor CVEs related to Python, Gunicorn, Debian and Caddy.
Use __Docker Scout__ or __Trivy__ to scan vulnerabilities

```bash
docker scout cves python:3.13.5-slim
```

Regenerate environment secrets periodically and rotate any hardcoded tokens or passwords.

## 7. Backup Strategy

### For SQLite

Back up the __instance/__ folder regularly.

```powershell
$date = Get-Date -Format "yyyy-MM-dd"
Copy-Item -Path "instance\users.db" -Destination "backups\users_$date.db"
```

or for bash

```bash
cp instance/app.db backups/app_$(date +%F).db
```

### For Docker volumes (if used in production)

```bash
docker run --rm --volumes-from flask_app -v $(pwd):/backup alpine tar cvf /backup/backup.tar /app/instance
```

```powershell
docker run --rm --volumes-from flask_app -v "${PWD}:/backup" alpine tar cvf /backup/backup.tar /app/instance
```

## 8. Troubleshooting Guide

Issue     ->    Diagnosis   ->  Fix
App not responding  ->  Check docker ps and docker logs web  ->  Restart containers

--------------------------------------------------------------------------------------------
Caddy shows 502 Bad Gateaway  ->  **web** container may not be ready ->  Run **docker compose logs**

--------------------------------------------------------------------------------------------------;

HTTPS not working   ->   Caddy TLS config issue  ->   Check **Caddyfile**, ensure domain is correct

----------------------------------------------------------------------------------------------------;

Tests fail on GitHub CI  -> Check **pytest** output in Actions logs  -> Fix test or broken app logic

-----------------------------------------------------------------------------------------------------'

Volume not persisting   ->  Check **docker-compose.yml** volume paths   -> Make sure paths map correctly.
