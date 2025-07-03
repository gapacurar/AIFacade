# Software Specification Document (SSD) for DeepSeek Chat Application

---

## 1. Document Control

- **Version:** 1.2
- **Date:** 2025-06-30
- **Authors:** [Your Team Name]
- **Status:** Draft

---

## 2. Introduction

2.1 **Purpose**

This Software Specification Document defines the functional and non-functional requirements, system architecture, interfaces, data models, and design constraints for the DeepSeek Chat Application. It serves as the single source of truth for developers, QA engineers, and stakeholders.

2.2 **Scope**

The system provides a secure, web-based chat interface where registered users can interact with the DeepSeek AI API. Chats are stored locally in a SQLite database, and users can clear their chat history. Administrative dashboards, production hardening, and advanced analytics are out of scope for v1.

2.3 **Definitions, Acronyms, and Abbreviations**

| Term/API   | Definition                                          |
| ---------- | --------------------------------------------------- |
| Flask      | Python microframework for web server and routing    |
| SQLAlchemy | ORM for database modeling and querying              |
| CSP        | Content Security Policy                             |
| CSRF       | Cross-Site Request Forgery protection via flask-wtf |
| CI/CD      | Continuous Integration and Continuous Deployment    |

---

## 3. Overall Description

3.1 **Product Perspective**

- A modular Flask application built using the factory pattern and Blueprints.

- Stores data locally in SQLite using Flask-SQLAlchemy.

- Runs inside Docker with Gunicorn and Caddy (self-signed certs for test environments).

- **Not production-ready:**

  - Only self-signed TLS certificates in test containers.
  - SQLite does not support concurrent writes or clustering.
  - No load balancing or container orchestration defined.
  - Lacks centralized logging, monitoring, and health checks.
  - No automated backup or disaster recovery processes.

3.2 **User Classes & Characteristics**

| User Type      | Characteristics                                                     |
| -------------- | ------------------------------------------------------------------- |
| End User       | Registers, logs in, submits prompts, views and clears chat history. |
| Admin (future) | Manages users and system health; out of scope for v1.               |

3.3 **Operating Environment**

- Linux container (Docker) running Python 3.13-5, Gunicorn, and Caddy.
- SQLite database persisted in a Docker volume.

3.4 **Design & Implementation Constraints**

- Must use Flask, Flask-SQLAlchemy, Flask-WTF, Flask-Login, and Flask-Limiter.
- Passwords hashed via Werkzeug security utilities.
- API key stored in environment variables; never in source code.

---

## 4 Functional Requirements

4.1 **Authentication & Authorization**

- **FR1:** User registration with unique username and password.
- **FR2:** Secure login and logout with session protection.
- **FR3:** Passwords stored hashed; plaintext passwords never stored.

4.2 **Chat Interface**

- **FR4:** Submit prompts via a web form on `/chat`.
- **FR5:** Call DeepSeek API with configured API key and return response.
- **FR6:** Persist chat entries (prompt, response, timestamp) linked to user.
- **FR7:** Display all chat history inline on the `/chat` page (no separate `/history` route). Pagination and keyword search are not yet supported.
- **FR8:** Allow users to clear their chat history, deleting all records for that user.

4.3 **Error Handling**

- **FR9:** Render custom 404 and 500 error pages.
- **FR10:** Gracefully handle API failures and display user-friendly messages.

---

## 5 Non-Functional Requirements

5.1 **Security**

- CSRF protection via Flask-WTF on all forms.
- HTTP security headers applied:
  - Content-Security-Policy
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Referrer-Policy: no-referrer
- Rate limiting: e.g., 30 prompts/hour per user via Flask-Limiter.
- Session protection via Flask-Login.

5.2 **Reliability & Availability**

- Application shall start reliably under Docker within acceptable startup times (TBD).
- API failures are surfaced to users with clear error messages; no automatic retries are implemented in this version.

5.3 **Scalability**

- Stateless Flask workers managed by Gunicorn; database migration needed for high-concurrency environments.

5.4 **Usability**

- Designed for desktop browsers; mobile responsiveness is untested (Bootstrap-based UI).

5.5 **Maintainability**

- Clear code separation with Blueprints and factory pattern.
- Target code coverage ≥ 98% using pytest.

---

## 6. System Architecture

6.1 **High-Level Block Diagram**

User Browser ↔ Caddy (HTTPS) ↔ Gunicorn Worker ↔ Flask App

- **Blueprints:** auth, chats
- **Extensions:** SQLAlchemy, WTForms, Flask-Login, Flask-Limiter

6.2 **Component Descriptions**

- **Auth Blueprint:** `/register`, `/login`, `/logout`.
- **Chat Blueprint:** `/chat` (prompt form, inline history, clear action).
- **Error Handlers:** Custom handlers for HTTP 404 and 500.
- **CLI Module:** `init-db`, `reset-db`, `clear-all` commands.

---

## 7. Data Model

7.1 **User Table**

| Field           | Type        | Constraints        |
| --------------- | ----------- | ------------------ |
| `id`            | Integer     | PK, auto-increment |
| `username`      | String(150) | Unique, not null   |
| `password_hash` | String(256) | Not null           |

7.2 **Chat Table**

| Field       | Type     | Constraints                     |
| ----------- | -------- | ------------------------------- |
| `id`        | Integer  | PK, auto-increment              |
| `user_id`   | Integer  | FK → user.id, on delete cascade |
| `prompt`    | Text     | Not null                        |
| `response`  | Text     | Not null                        |
| `timestamp` | DateTime | Defaults to current timestamp   |

---

## 8. API Interfaces

8.1 **Web Endpoints**

| Method | Endpoint    | Description                                     |
| ------ | ----------- | ----------------------------------------------- |
| GET    | `/register` | Render registration form                        |
| POST   | `/register` | Handle user signup                              |
| GET    | `/login`    | Render login form                               |
| POST   | `/login`    | Authenticate user                               |
| GET    | `/logout`   | Logout user and redirect                        |
| GET    | `/chat`     | Render chat interface with inline history       |
| POST   | `/chat`     | Submit prompt, call API, store & display result |
| POST   | `/clear`    | Clear user's chat history and reload `/chat`    |

8.2 **External API**

- **DeepSeek API**
  - **Endpoint:** `https://api.deepseek.com/v1/chat/completions`
  - **Method:** POST
  - **Headers:**
    - `Content-Type: application/json`
    - `Authorization: Bearer <DEEPSEEK_API_KEY>`
  - **Body:**

    ```json
    {
      "model": "deepseek-chat",
      "messages": [{"role": "user", "content": "<prompt>"}]
    }
    ```

  - **Response Handling:**

    ```python
    if response.status_code == 200:
        result = response.json()
        return markdown(result["choices"][0]["message"]["content"])
    else:
        # Log error and display message to user
    ```

---

## 9. Security Considerations

- API key stored in environment variable; use Docker secrets for production.
- Hardened HTTP headers via `@app.after_request` decorator.

---

## 10. Constraints and Assumptions

- DeepSeek API SLAs and uptime are external dependencies.
- SQLite is used for v1; plan migration to a client-server DBMS.
- Test environments use self-signed certs; production requires valid TLS.

---

## 11. Appendix

- A. Flask extensions and versions
- B. Database schema SQL scripts
- C. Environment variable definitions

---

*End of Software Specification Document.*
