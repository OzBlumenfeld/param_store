# Secure Parameter Store

A self-hosted secrets management service inspired by AWS SSM Parameter Store. Store, retrieve, and manage sensitive configuration values (API keys, passwords, connection strings, etc.) with per-user access control and envelope encryption.

## What it does

- Users register and authenticate via JWT tokens
- Each user can store named parameters scoped to an application label (defaults to `"default"`)
- Parameter values are encrypted at rest using **envelope encryption**: each value gets a unique Data Encryption Key (DEK), and the DEK itself is encrypted with a master key derived via PBKDF2 + Fernet
- Full CRUD via a REST API, with a React frontend for browsing and managing parameters

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14+, FastAPI, SQLAlchemy, Alembic |
| Frontend | React 19, TypeScript, Vite, Axios |
| Database | PostgreSQL 15 |
| Auth | JWT (PyJWT), password hashing via Argon2/bcrypt (passlib) |
| Encryption | Python `cryptography` library (Fernet + PBKDF2HMAC) |
| Package manager | [uv](https://github.com/astral-sh/uv) |

## Project structure

```
param_store/
├── app/
│   ├── api/            # FastAPI routers (auth, parameters)
│   ├── core/           # Config, DB engine, logger
│   ├── models/         # SQLAlchemy models (User, Parameter)
│   └── services/       # Business logic (auth, encryption, parameter CRUD)
├── alembic/            # Database migrations
├── frontend/           # React/TypeScript app
├── tests/              # pytest suite (runs against SQLite in-memory)
├── main.py             # App entry point (port 8181 in dev)
├── Dockerfile          # Production image
└── docker-compose.yml  # Spins up PostgreSQL
```

## Running locally

### 1. Start PostgreSQL

```bash
docker compose up -d
```

This starts a PostgreSQL 15 instance on port `5432` with:
- User: `postgres`
- Password: `postgres`
- Database: `postgres`

### 2. Set up environment variables

Create a `.env` file in the project root (see the env vars section below).

### 3. Install dependencies and run migrations

```bash
# Install uv if you don't have it: https://github.com/astral-sh/uv
uv sync
uv run alembic upgrade head
```

### 4. Start the backend

```bash
uv run python main.py
```

API available at `http://localhost:8181`. Interactive docs at `http://localhost:8181/docs`.

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:5173` (default Vite port).

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | *(required)* |
| `MASTER_ENCRYPTION_KEY` | Master key used to encrypt/decrypt DEKs | *(required)* |
| `SECRET_KEY` | Secret used to sign JWT tokens | *(required in prod)* |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry in minutes | `30` |

## Running tests

Tests use an in-memory SQLite database — no running Postgres required.

```bash
uv run pytest
```

## API overview

All `/params` endpoints require a `Bearer` token in the `Authorization` header.

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user, returns JWT |
| `POST` | `/auth/login` | Login, returns JWT |
| `POST` | `/params/` | Create a parameter |
| `GET` | `/params/` | List parameters (filter by `app`, `name`, or fetch all values) |
| `GET` | `/params/{name}` | Get and decrypt a single parameter |
| `PUT` | `/params/{name}` | Update a parameter value |
| `DELETE` | `/params/{name}` | Delete a parameter |

Parameters are keyed by `(user_id, app, name)`. The `app` field defaults to `"default"` and lets you namespace parameters per application.

## How encryption works

1. When a parameter is saved, a random **Data Encryption Key (DEK)** is generated.
2. The parameter value is encrypted with the DEK using Fernet (AES-128-CBC + HMAC).
3. The DEK is then encrypted with the **Master Key** (derived from `MASTER_ENCRYPTION_KEY` via PBKDF2-SHA256) and stored alongside the encrypted value.
4. On retrieval, the process is reversed: decrypt the DEK with the master key, then decrypt the value with the DEK.

This means rotating the master key only requires re-encrypting the stored DEKs, not every parameter value.
