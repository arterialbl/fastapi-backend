# FastAPI User Management API

REST API built with FastAPI, PostgreSQL, SQLAlchemy and Docker.

## Features

- JWT Authentication
- Refresh Tokens
- Logout with token revocation
- Role-Based Access Control (RBAC)
- Users CRUD
- Notes CRUD
- Pagination and filtering
- Alembic migrations
- Docker support

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Pydantic

## Run with Docker

bash docker compose up --build 

## Environment Variables

Create .env file:

env DATABASE_URL= SECRET_KEY= ALGORITHM=HS256 ACCESS_TOKEN_EXPIRE_MINUTES=30 REFRESH_TOKEN_EXPIRE_DAYS=7 

## API Documentation

Swagger UI:

txt http://localhost:8000/docs 