# User Guide Document

## Document Control

- **Version:** 1.0
- **Date:** 2025-06-30
- **Authors:** Bicu Andrei Ovidiu
- **Status:** Final

## Table of Contents

1. Introduction
2. Getting Started
    - Prerequisites
    - Installation
3. Running the Application
4. Accessing the App
5. Testing
6. Common Issues
7. Backup & Restore

## 1. Introduction

This guide explains how to install, run and use the Flask-based web application deployed with Docker and reverse-proxied via Caddy. The app supports automatic testing via GitHub Actions and is structured for production use with Gunicorn.

## 2.1 Prerequisites

Make sure you have the following installed:

- Docker
- Docker Compose
- Git
- (Optional) Python 3.x for development outside containers

## 2.2 Installation

Clone the repository

```sh
git clone --branch final-exam https://github.com/your-username/AIFacade.git
cd AIFacade
```

If this will move to main then:

```sh
git clone https://github.com/your-username/AIFacade.git
cd AIFacade
```

Configure environment variables:

Create a *.env* file IF *it doesn't exist already*:

```env
SECRET_KEY = supersecretkey
DATABASE_URI = sqlite:///users.db
DEEPSEEK_API_KEY = yourapikey
```

The DEEPSEEK_API_KEY can be generated from <https://platform.deepseek.com/api_keys>
Configure the database using CLI commands if there is no __instance/users.db__ in your root directory.

```sh
flask --app project init-db
```

This will create the __instance__ directory and the database alongside with the tables needed.

## 3. Running the Application

Run the application using Docker Compose:

```sh
docker compose up --build
```

This builds the image and starts:

__web__: Flask app served via Gunicorn
__caddy__: Reverse proxy

## 4. Accessing the Application

After startup:
    - Local access (HTTP): <http://localhost>
    - HTTPS (self-signed): <https://localhost>
Note: On first access, your browser will show a security warning. Accept the risk to continue.

## 5. Testing

## Docker

To run tests locally in the container:

```sh
docker compose run --rm web pytest tests/ -v
```

## Terminal

To run tests locally outside docker:

```sh
python -m pytest --cov=project tests/ -v
```

To generate a html report:

```sh
python -m pytest --cov=project --cov-report=html tests/
```

After that a folder called "htmlcov" should appear in your root directory. Also the output should give you an url on which you can click to open the report up.

## 6. Common Issues

Port in use?
```docker compose down```

Volume not persisting?
Ensure **instance/** is mounted in **docker-compose.yml**

## 7. Backup

```powershell
$date = Get-Date -Format "yyyy-MM-dd"
Copy-Item -Path ".\instance\users.db" -Destination ".\backups\users_$date.db"
```

This will create a folder "backups" in your root directory which contains the backups you make.
