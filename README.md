# 📰 News Publishing Platform

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6-success?logo=django)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.17-red)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Sphinx](https://img.shields.io/badge/Sphinx-Documentation-orange)

A role-based news publishing platform built with **Django**, **Django REST Framework**, **Docker**, and **Sphinx**.

---

# Table of Contents

- Overview
- Features
- Technology Stack
- System Architecture
- User Roles
- Database Models
- REST API
- Installation
- Docker
- Project Structure
- Documentation
- Testing
- Security
- Roadmap
- Contributing
- Author
- License

---

# Overview

This application simulates a real-world editorial workflow.

Journalists create articles, editors review and approve content, publishers manage publications, and readers subscribe to publishers or journalists to receive approved news.

---

# Features

## Authentication
- Custom Django User model
- Login & Logout
- User Registration
- Token Authentication
- Role-based authorization

## Content Management
- Create articles
- Edit articles
- Delete articles
- Article approval workflow
- Newsletter management
- Publisher management

## Reader Features
- Subscribe to publishers
- Subscribe to journalists
- Browse approved articles
- Read newsletters

## Notifications
- Email notifications after approval
- Internal approval logging API

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.14 |
| Framework | Django 6 |
| API | Django REST Framework |
| Database | SQLite (MariaDB Ready) |
| Documentation | Sphinx |
| Containerization | Docker |
| Testing | pytest |

---

# System Architecture

```text
Client
   │
   ▼
Django Views / REST API
   │
Business Logic
   │
Django ORM
   │
SQLite Database
```

---

# User Roles

| Role | Permissions |
|------|-------------|
| Reader | Read approved articles, subscribe |
| Journalist | Create/edit/delete own articles, newsletters |
| Editor | Review and approve articles |
| Publisher | Manage publications, editors, journalists |

---

# Database Models

- CustomUser
- Publisher
- Article
- Newsletter
- ApprovedArticleLog

---

# REST API

| Method | Endpoint |
|---------|----------|
| POST | `/api/token/` |
| GET/POST | `/api/articles/` |
| GET | `/api/articles/subscribed/` |
| GET/PUT/DELETE | `/api/articles/{id}/` |
| GET/POST | `/api/newsletters/` |
| POST | `/api/approved/` |

---

# Installation

```bash
git clone https://github.com/your-username/news-publishing-platform.git
cd news-publishing-platform

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Application:

```
http://127.0.0.1:8000
```

---

# Docker

Build:

```bash
docker build -t django-capstone .
```

Run:

```bash
docker run --rm -p 8000:8000 django-capstone
```

---

# Project Structure

```text
news_project/
├── docs/
├── news/
├── news_project/
├── Dockerfile
├── requirements.txt
├── manage.py
└── README.md
```

---

# Documentation

Generate documentation:

```bash
cd docs
make html
```

Output:

```
docs/build/html/index.html
```

---

# Testing

```bash
python manage.py test
pytest
```

---

# Security

- Django authentication
- Token authentication
- Role-based permissions
- ORM protection against SQL injection
- CSRF protection
- Form and serializer validation

---

# Roadmap

- Image uploads
- Rich text editor
- Categories
- Search
- Comments
- Swagger/OpenAPI
- GitHub Actions
- PostgreSQL support
- Docker Compose
- Cloud deployment

---

# Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

# Author

**Hamza Massaoui**

Software Engineer

---

# License

MIT License