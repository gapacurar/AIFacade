# User Guide Document

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
* Docker
* Docker Compose
* Git
* (Optional) Python 3.x for development outside containers

## 2.2 Installation
1. Clone the repository
```sh
git clone --branch final-exam https://github.com/your-username/AIFacade.git
cd AIFacade
```
* If this will move to main then:
```sh
git clone https://github.com/your-username/AIFacade.git
cd AIFacade
```
2. Configure environment variables:
Create a __.env__ file IF **it doesn't exist already**:
```env
SECRET_KEY = supersecretkey
DATABASE_URI = sqlite:///users.db
DEEPSEEK_API_KEY = yourapikey
```
## 3. Running the Application
Run the application using Docker Compose:
```sh
docker compose up --build
```
This starts:
__web__: Flask app served via Gunicorn
__caddy__: Reverse proxy

## 4. Accessing the App
After startup:
    - Local access (HTTP): http://localhost
    - HTTPS (self-signed): https://localhost
* Note: On first access, your browser will show a security warning. Accept the risk to continue.

## 5. Testing
Port in use?
```docker compose down```

Volume not persisting?
Ensure __instance/__ is mounted in __docker-compose.yml__

## 6. Backup
Option 1: Manual copy
```powershell
$date = Get-Date -Format "yyyy-MM-dd"
Copy-Item -Path ".\instance\users.db" -Destination ".\backups\users_$date.db"
```
Option 2: Docker volume archive
```powershell
docker run --rm --volumes-from flask_app -v "${PWD}:/backup" alpine tar cvf /backup/backup.tar /app/instance
```
