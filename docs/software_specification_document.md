# Software Specification Document (SSD) for AIFacade Application

---

## 1. Document Control

- **Version:** 1.2
- **Date:** 2025-07-17
- **Authors:** Bicu Andrei Ovidiu
- **Status:** Final

---

## 2. Introduction

2.1 **Purpose**

This Software Specification Document defines the functional and non-functional requirements, system architecture, interfaces, data models, and design constraints for the AIFacade Application. It serves as the single source of truth for developers, QA engineers, and stakeholders.

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

At its core, the AIFacade Application is built using a modular Flask structure that leverages the factory pattern and Blueprints to separate concerns. All user data, including credentials and chat logs, is stored in a local SQLite database. The application runs inside a Docker container and uses Gunicorn as the WSGI HTTP server. For secure transport, it relies on a Dockerized instance of the Caddy server, which provides HTTPS using self-signed certificates in development environments.

- **Not production-ready:**

 It’s important to note that the system, in its current state, is not intended for public-facing or production use. Self-signed certificates, the lack of distributed database support, the absence of load balancing, and no defined orchestration or automated recovery mechanisms make it more appropriate for local and test deployments.

3.2 **User Classes & Characteristics**

There are two primary user types. The end user can register an account, log in, submit prompts to the AI, and view or clear their chat history. While the application anticipates future support for administrative users who would manage accounts and oversee system health, that role remains out of scope for version one.

| User Type      | Characteristics                                                     |
| -------------- | ------------------------------------------------------------------- |
| End User       | Registers, logs in, submits prompts, views, and clears chat history. |
| Admin (future) | Manages users and system health; out of scope for v1.               |

3.3 **Operating Environment**

The app is designed to run inside a Linux-based Docker container using Python 3.13, managed by Gunicorn and secured via Caddy. SQLite provides lightweight local data persistence, stored in Docker volumes.

3.4 **Design & Implementation Constraints**

Several technologies and constraints define the system boundaries. Flask and its ecosystem are mandatory, including extensions for login, forms, and rate limiting. Passwords are securely hashed using Werkzeug utilities. All API keys are stored via environment variables to ensure they are never embedded in the source code.

## 4 Functional Requirements

4.1 **Authentication & Authorization**

Users begin by registering with a unique username and password. Their credentials are securely hashed before storage, and plaintext passwords are never stored. We use session protection for secure login and logout logic. After logging in, they are redirected to the chat interface, where they can submit prompts

4.2 **Chat Interface**

Each submission is sent to the DeepSeek API, and the response is returned to the browser while also being saved in the local database along with the prompt and timestamp. The /chat route doubles as a chat log, displaying all prior conversations inline. Users may also choose to clear their entire chat history with a single action. Searching and pagination are not included in this release.

4.3 **Error Handling**

The system includes graceful error handling. If a user navigates to a missing page or an internal error occurs, custom 404 and 500 error pages are shown. If the DeepSeek API fails to respond, a friendly error message is presented instead of raw exceptions.

## 5 Non-Functional Requirements

5.1 **Security**

Security is a top priority. All forms are protected with CSRF tokens via Flask-WTF. The application enforces strong HTTP headers including Content Security Policy, no-referrer settings, X-Frame-Options, and anti-sniffing rules. Users are limited to a maximum number of interactions per hour to mitigate abuse, enforced by Flask-Limiter. Session management is handled securely through Flask-Login. Input validation is offered via Pydantic using predefined schemas.

5.2 **Reliability & Availability**

The application is expected to start up reliably inside Docker containers and provide clear error messaging when the DeepSeek API is unavailable. Automated retries are not implemented in this version.

5.3 **Scalability**

While the app uses stateless Gunicorn workers for concurrent request handling, the underlying SQLite database limits its scalability. Moving to a full-fledged client-server DBMS will be necessary for any future scaling.

5.4 **Usability**

The interface is designed primarily for desktop use, using Bootstrap for layout. Mobile support is untested but could be added with minor UI adjustments.

5.5 **Maintainability**

The codebase is modular and easy to understand, leveraging Blueprints to separate authentication and chat functionalities. A high standard for test coverage (99% and above) ensures changes can be made confidently with minimal risk of regression.

## 6. System Architecture

The data flow begins with a user accessing the web interface through their browser. The request passes through Caddy, which handles HTTPS transport, before reaching the Gunicorn application server. Gunicorn forwards the request to the Flask app, which processes it via its modular components.
Authentication and chat functionality are each contained in separate Blueprints. Custom error handlers catch and render user-friendly pages when something goes wrong. A CLI module supports administrative actions such as initializing or resetting the database and wiping all chat data.

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

The system defines two primary tables.

The User table stores each account with a unique ID, a username, and a hashed password. The Chat table contains individual chat entries, each linked to a user ID. Every chat record includes the original prompt, the AI's response, and a timestamp indicating when the interaction occurred. If a user is deleted, their associated chat entries are also removed via cascading foreign key behavior.

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

## 8. API Interfaces

8.1 **Web Endpoints**

The application exposes several web-facing endpoints. Users access the /register route to create an account and /login to authenticate. The /logout route ends the session. The core functionality resides at /chat, where users both submit new prompts and view past conversations. A separate /clear endpoint allows users to delete their entire chat history in one step.

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

To fulfill its AI features, the system connects to the DeepSeek API using a secure POST request. The prompt is sent in JSON format, and if the request is successful, the system parses and renders the response using Markdown. Errors are logged and result in user-friendly messages, never raw traces or broken pages.

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

## 9. Security Considerations

Security is woven into the application at every level. The DeepSeek API key is stored only in environment variables, and in future deployments, should be managed through Docker secrets or a similar mechanism. HTTP headers are programmatically enforced after every response, providing strong browser-level safeguards.

## 10. Constraints and Assumptions

The application assumes high availability of the DeepSeek API and does not currently support fallback or caching mechanisms. SQLite, while sufficient for local deployments, will eventually need to be replaced by a more scalable database. Additionally, while development environments use self-signed certificates, production deployments will require valid TLS certificates for real-world usage.

## 11. Appendix

Included are reference materials such as a list of Flask extensions used and their versions, SQL scripts for creating the database schema, and a description of all required environment variables.

*End of Software Specification Document.*
