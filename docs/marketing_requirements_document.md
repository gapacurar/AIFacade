# Marketing Requirements Document (MRD)

## Document Control

- **Version:** 1.0
- **Date:** 2025-07-17
- **Authors:** Bicu Andrei Ovidiu
- **Status:** Final

## 1. Executive

Our product is a secure, easy-to-use chatbot web application powered by an AI model via a modular API interface (currently using DeepSeek). It enables users to create accounts, log in, and interact with an AI assistant through a simple web interface. The application focuses on privacy, security, and developer-friendly deployment via Docker.

---

## 2. Market Overview

The current market for AI-powered chatbots is dominated by SaaS platforms and proprietary cloud services. While these offerings are rich in features, they often fail to address the needs of developers and teams looking for a lightweight, secure, and self-hosted alternative. Our solution addresses that specific gap.

### 2.1 Target Market

The primary targets are developers and AI enthusiasts who want to experiment with chatbot APIs, small teams or startups seeking a lightweight, self-hosted chatbot platform, educational institutions or hobbyists learning secure web app development, and users requiring local deployment without dependency on third-party SaaS.

### 2.2 Market Needs

The market demands an intuitive registration and login system, secure data handling, dependable integration with modern AI APIs, and a robust yet simple setup process. Developers, in particular, prefer open-source or containerized applications that can run locally or in development environments, with HTTPS enabled for enhanced security. These requirements are seldom fully addressed by existing solutions.

### 2.3 Competitor Analysis

Most competitors are cloud-only and do not allow local data storage or user management. By contrast, this application stands out through its unique combination of local hosting, robust security features, and full control over user data, all without compromising ease of use or extensibility.

## 3. Product Description

The application offers a focused and secure environment for chatting with an AI assistant powered by the DeepSeek API. Users can create accounts, securely log in, and engage in AI conversations through a web-based interface.

### 3.1 Key Features

Key capabilities include secure password storage with hashing, session management with hardened cookies, and protection against CSRF attacks. Users can submit prompts and access their individual chat histories, which are stored locally on their device. The application supports Markdown rendering for AI responses, ensuring readability and formatting. Abuse is mitigated through rate limiting, and HTTPS is provided using a Dockerized Caddy server with self-signed certificates for development purposes. The architecture is modular, allowing developers to easily customize or extend the platform. With nearly complete test coverage, the application emphasizes reliability and robustness.

### 3.2 Benefits

The product offers distinct advantages: user data and prompts remain entirely local, reducing the risks of data leaks or third-party exposure. Its security-focused design mitigates common web threats, while Docker-based deployment ensures that even beginners can get started quickly. By avoiding cloud-based dependencies, the platform eliminates recurring fees and grants full freedom to its users.

## 4. Marketing Strategy

### 4.1 Positioning

Positioned as a secure and developer-friendly chatbot platform, the application appeals to those who value privacy, control, and simplicity. It is ideal for experimentation, education, and lightweight deployment scenarios. Its open architecture encourages contributions and adaptations, making it more than just a tool—it’s a foundation for innovation.

### 4.2 Pricing

The platform is available free of charge under an open-source license, and while current plans are entirely community-driven, the door remains open for future hosted or premium service offerings. These could cater to non-technical users or organizations requiring managed deployments.

### 4.3 Promotion & Distribution

Promotion will focus on outreach to developer-centric communities such as Reddit, Hacker News, and Dev.to. Blog content will highlight setup instructions, use cases, and security principles. The application will live on GitHub, with Docker images hosted on Docker Hub for instant deployment via Docker Compose. Tutorials and walkthroughs will support onboarding, and community involvement will be encouraged through issue tracking and pull requests.

- Share on developer forums (Reddit, Hacker News, Dev.to).
- Publish blog posts demonstrating setup and use cases.
- Offer a GitHub repository with detailed documentation and tutorials.
- Engage in community-driven improvements.

## 5. Requirements & Constraints

### 5.1 Technical Requirements

From a technical standpoint, the platform requires Python 3.10 or higher and uses Docker for deployment, including HTTPS support. Users must supply a valid DeepSeek API key, which is securely stored. Compatibility with all major modern browsers ensures a smooth user experience.

### 5.2 Legal & Compliance

In terms of legal and compliance concerns, the platform is designed with minimal data collection. Only usernames and passwords are stored, and even then, passwords are hashed securely. There is no built-in analytics or third-party tracking to compromise user privacy.

### 5.3 Considerations

A few considerations must be acknowledged. While the platform is secure, it is not yet hardened for production deployment in public-facing environments. TLS is currently supported through self-signed certificates, appropriate for local or development use only. Features such as multi-factor authentication or email verification are not yet included.

## 6. Success Metrics

The impact of this project will be measured through a variety of community and technical indicators. GitHub stars and forks will reflect interest and adoption. Docker image pull counts will signal deployment traction. Active participation through GitHub issues and pull requests will provide insight into community engagement.

In addition, the platform will be continuously monitored for test coverage and continuous integration (CI) build health, helping ensure the codebase remains stable and trustworthy.

## 7. Future Opportunities

Looking forward, several enhancements are already envisioned. Production-ready deployment guides, including instructions for configuring trusted HTTPS certificates, will help transition from development to real-world use. Multi-tenant support and administrative dashboards could expand the platform’s scope for team-based use cases. Additional security measures, such as input sanitization and prompt filtering, are planned to further reinforce the system.

Eventually, the possibility of offering a hosted SaaS version, aimed at users without technical backgrounds, may bring the platform to an even broader audience.

## Appendix

### User Personas

Dave is a developer who needs a safe and private space to experiment with AI chatbots. He values secure architectures and wants full control over his tools.

Stella leads a small startup team looking for an affordable chatbot interface that doesn’t tie them to a commercial SaaS provider. She needs something that just works out of the box.

Sam is a student learning web development and AI integration. For him, the platform is both a teaching tool and a playground—open, inspectable, and safe.

## Glossary

| Term                  | Definition                                                                                                               |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| **Chatbot**           | A software application used to conduct an online conversation via text or text-to-speech, typically powered by AI.        |
| **AI Model**          | An artificial intelligence system trained to perform tasks such as natural language processing, in this case, for generating chatbot responses. |
| **API (Application Programming Interface)** | A set of rules and protocols for building and interacting with software applications, allowing external systems to communicate with the AI. |
| **Modular API Interface** | A flexible and interchangeable API design that allows easy replacement or extension of the AI model.                    |
| **Docker**            | A platform for developing, shipping, and running applications using containerization, which ensures consistency across environments. |
| **Docker Compose**    | A tool used to define and run multi-container Docker applications using a YAML configuration file.                         |
| **Caddy Server**      | A modern, lightweight web server with automatic HTTPS support, used in this platform to serve the chatbot interface.       |
| **Self-signed Certificates** | SSL/TLS certificates generated locally rather than issued by a Certificate Authority, used primarily for development purposes. |
| **CSRF (Cross-Site Request Forgery)** | A type of malicious exploit of a website where unauthorized commands are transmitted from a user that the web application trusts. |
| **Session Management**| Techniques for maintaining state and authentication between the client and the server during interaction.                 |
| **Rate Limiting**     | A technique used to control the amount of incoming requests to prevent abuse or overuse of system resources.              |
| **Markdown**          | A lightweight markup language used to format text, such as bold, lists, and headers, in AI responses.                     |
| **Open Source**       | Software with source code that anyone can inspect, modify, and enhance.                                                    |
| **SaaS (Software as a Service)** | Software that is licensed on a subscription basis and is centrally hosted, typically not locally deployable.         |
| **Test Coverage**     | A measure of how much of the codebase is exercised by automated tests.                                                    |
| **CI (Continuous Integration)** | A development practice where developers integrate code into a shared repository frequently, each integration verified by automated builds and tests. |
| **HTTPS (HyperText Transfer Protocol Secure)** | A protocol for secure communication over a computer network, often using TLS.                              |
| **Multi-tenant Support** | A software architecture where a single instance serves multiple user groups or clients (tenants) with isolated data and configurations. |
