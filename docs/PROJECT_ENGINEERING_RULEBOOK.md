final?
📘 SamvaadAI
Project Engineering Rulebook

Internal Engineering Handbook

1. Project Overview
Project Name

SamvaadAI

Vision

Build an AI-powered conversational platform with:

Clean architecture

Scalable backend

Strong collaboration workflow

Professional engineering standards

Purpose of This Document

This handbook defines:

Development standards

Collaboration workflow

Deployment expectations

Code quality rules

Team responsibilities

🚫 No deviation without team agreement.

2. Standardized Development Environment
2.1 Required Versions
Technology	Required Version
Python	3.10+
Node.js (Frontend)	18+
Git	Latest stable
Docker	Optional but recommended

✅ All developers must use the same major versions.

2.2 Fixed Ports

To avoid conflicts:

Service	URL
Backend (FastAPI)	http://localhost:8000

Frontend	http://localhost:3000

These ports are reserved for this project.

2.3 API Base URL
Local
http://localhost:8000/api/v1
Production
https://your-domain.com/api/v1

🚫 Never hardcode API URLs in the frontend.
✅ Always use environment variables.

2.4 Environment Variables
Backend .env
APP_ENV=development
PORT=8000
OPENAI_API_KEY=your_key
DATABASE_URL=your_db_url
Frontend .env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
Environment Rules

❌ Never commit .env

✅ Add .env to .gitignore

✅ Production keys must never be used in development

3. Folder Structure Convention
Backend
backend/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── core/
│   └── main.py
│
├── tests/
├── requirements.txt
└── .env
Frontend
frontend/
│
├── components/
├── pages/
├── services/
├── hooks/
├── utils/
└── public/
Rule

❌ No random files at project root.

4. Git & Version Control Workflow
4.1 Branching Strategy
Branch	Purpose
main	Production-ready code
dev	Integration branch
feature/*	Individual feature development
Feature Branch Examples
feature/chat-ui
feature/nlp-engine
feature/api-integration

❌ No direct commits to main.

4.2 Workflow
main
  ↑
dev
  ↑
feature/*
Steps

Create feature branch from dev

Push feature branch

Open Pull Request (PR) to dev

Test

Merge dev → main

All PRs must be linked to an Issue.

4.3 Commit Message Convention
Format
type: short description
Types
Type	Purpose
feat	New feature
fix	Bug fix
refactor	Code improvement
docs	Documentation
chore	Maintenance
Examples

✅ Good:

feat: add NLP preprocessing module
fix: resolve CORS issue in FastAPI

❌ Bad:

update
changes
final
done
4.4 Pull Request Rules

Each PR must include:

What was implemented

Why it was implemented

Screenshots (for UI changes)

Testing steps

PR Checklist

✔ Code runs locally
✔ No hardcoded values
✔ No console debug logs
✔ No unused imports

5. Commands for Team Sync
Create Feature Branch
git checkout dev
git pull origin dev
git checkout -b feature/feature-name
Push Changes
git add .
git commit -m "feat: add chat endpoint"
git push origin feature/feature-name
Sync with Latest Dev
git checkout dev
git pull origin dev
git checkout feature/feature-name
git merge dev

⚡ Resolve conflicts locally before creating PR.

6. Deployment & Build Rules
Run Backend Locally
uvicorn app.main:app --reload --port 8000
Run Frontend Locally
npm install
npm run dev
Production Build (Frontend)
npm run build
Environment Rules

Use clear separation:

Development

Production

🚫 Never mix production keys with development.

Basic CI/CD Expectations

Code must run before PR

No breaking API contract changes

Lint before pushing

All endpoints manually tested

7. Common Mistakes to Avoid

❌ Hardcoded URLs
❌ Hardcoded API keys
❌ Breaking API response format
❌ Direct push to main
❌ Large unreviewed commits
❌ Unused code
❌ Debug prints in production

8. Team Responsibilities
Frontend Team

UI consistency

API integration

Error display

Loading states

❌ No backend logic

Backend Team

API structure

Validation

Error handling

Logging

Security checks

API Contract Ownership

Backend defines:

Request format

Response format

Status codes

Frontend must confirm before assuming changes.

Testing Responsibilities

Each developer must test:

Their feature

Integration with system

Minimum:

Manual API testing

Frontend integration testing

Documentation Expectations

Every new feature must include:

Short README update

API route documentation

Example request & response

9. Professional Engineering Standards
Naming Conventions
Item	Rule
Functions	snake_case
Classes	PascalCase
Constants	UPPER_CASE
Files	lowercase_with_underscores
Code Structure

Business logic → services

API logic → routes

Avoid files > 300 lines

Logging

✅ Use structured logging
❌ No print() in production

Log:

Errors

Warnings

Important events

Error Handling

Every endpoint must:

Handle invalid input

Return proper HTTP status codes

Avoid exposing internal stack traces

Security Basics

Validate all inputs

Use environment variables

Enable CORS properly

Never expose secrets

Apply rate limiting if possible

10.Issue Management Policy

Add this:

Issue Rules

Every task must start as an Issue.

No coding without issue reference.

Every PR must reference an issue.

Issues must be closed via PR merge.

Example:

Closes #12
Fixes #15


11. Engineering Culture

We operate as:

✅ Accountable engineers
✅ Clear communicators
✅ Professional collaborators

🚫 No “It works on my machine” excuses.

🔥 Final Statement

SamvaadAI will be built as:

A scalable, maintainable, production-ready AI system —
not a casual college submission.


Version: 1.0  
Last Updated: February 2026  
Owner: SamvaadAI Core Team