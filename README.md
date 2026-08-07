# Auth Service

This is a JWT authentication microservice built with FastAPI.

## Architecture
This service uses FastAPI for the web framework, SQLAlchemy for the ORM, and Passlib for password hashing. It supports user registration, login, token refresh, and role-based access control.

## Endpoints
- **POST /register**: Register a new user. Expects a JSON body with `username` and `password`.
- **POST /login**: Log in a user and receive a JWT token. Expects a JSON body with `username` and `password`.
- **POST /token/refresh**: Refresh the JWT token. Requires a valid token.

## Requirements
- FastAPI
- Uvicorn
- SQLAlchemy
- Passlib[bcrypt]
