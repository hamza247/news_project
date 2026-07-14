# Capstone Project - Django News Application

## Overview

This project is a Django-based news application. It allows readers to view approved articles, journalists to create articles and newsletters, and editors to review and approve submitted articles.

The application includes:

- Custom user roles
- Group-based permissions
- Article publishing workflow
- Newsletters
- RESTful API
- Token authentication
- Email notification
- Internal API logging
- Automated unit tests
- MariaDB configuration support

## User Roles

### Reader

Readers can:

- View approved articles
- View newsletters
- Subscribe to publishers
- Subscribe to journalists

### Journalist

Journalists can:

- Create articles
- Create newsletters
- View their content
- Update or delete their own articles

Articles submitted by journalists must be approved by an editor before they are visible to readers.

### Editor

Editors can:

- View submitted articles
- Approve articles
- Update articles
- Delete articles
- Create and manage newsletters

## Models

### CustomUser

Extends Django's default user model and adds a role field.

Roles:

- reader
- journalist
- editor

Reader-related fields:

- subscribed_publishers
- subscribed_journalists

### Publisher

Represents a curated news publication.

A publisher can have:

- multiple editors
- multiple journalists
- multiple subscribed readers

### Article

Represents a news article.

Fields include:

- title
- content
- author
- created_at
- approved
- publisher

### Newsletter

Represents a curated collection of articles.

Fields include:

- title
- description
- author
- articles
- created_at

### ApprovedArticleLog

Stores approved article logs sent to the internal REST API endpoint.

## Database Normalization

The database design follows normalization principles.

### First Normal Form

All model fields contain atomic values.

### Second Normal Form

Each non-key field depends on the primary key of its table.

### Third Normal Form

Related data is separated into different tables.

Examples:

- User data is stored in CustomUser.
- Publisher data is stored in Publisher.
- Article data is stored in Article.
- Newsletter data is stored in Newsletter.
- Many-to-many relationships are used for subscriptions and newsletter articles.

## UI/UX Planning

The user interface is simple and role-focused.

### Pages

- Home page
- Create article page
- Create newsletter page
- Editor review page
- Article approval page

### Design Goals

- Clear navigation
- Simple approval workflow
- Easy article reading experience
- Separate actions based on user role
- Minimal interface to reduce user confusion

## REST API Endpoints

### Authentication

```text
POST /api/token/