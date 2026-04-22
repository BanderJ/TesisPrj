# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI web application for managing coffee farmers ("caficultores") at a cooperative, including registration, document validation, and socio conversion workflows. Uses server-rendered Jinja2 templates for the UI.

## Development Commands

```bash
# Install dependencies (activate venv first)
python -m venv .venv
source .venv/Scripts/activate   # Windows
pip install -r requirements.txt

# Run the development server
uvicorn src.main:app --reload

# Compile TailwindCSS (watch mode)
./tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

App runs at `http://localhost:8000`. No test suite exists.

## Architecture

The project uses a four-layer pattern — every feature has a file in each layer:

| Layer | Path | Responsibility |
|---|---|---|
| **Routes** | `src/routes/` | HTTP endpoints, calls services, returns templates or JSON |
| **Services** | `src/services/` | Business logic, orchestrates models, owns transaction commit/rollback |
| **Models** | `src/models/` | Raw SQL via psycopg2, accepts optional `db` connection for shared transactions |
| **Schemas** | `src/schemas/` | Pydantic request/response models and input validation |

### Database

Direct psycopg2 (no ORM). The `Connection` class in [src/database/bd.py](src/database/bd.py) wraps a single connection per request with `autocommit=False` and `RealDictCursor`. Methods: `obtener()`, `obtener_uno()`, `ejecutar()`, `commit()`, `rollback()`.

Database credentials are hardcoded in [src/config.py](src/config.py) — `SECRET_KEY` reads from env, but `DB_*` values are literals.

Schema is in [src/database/script.sql](src/database/script.sql).

### Authentication

JWT stored as an httponly cookie (`access_token: "Bearer <token>"`). Passwords hashed with Argon2. All routes except `/auth/login` depend on `obtener_usuario_actual()` from [src/utilities/jwt_required.py](src/utilities/jwt_required.py), which raises `RequerirLoginException` → global exception handler → redirect to `/auth/login`. Token payload contains `personal_id`, `usuario`, `rol`, `nombre`, `exp` (7-day TTL).

### Transaction Pattern

When a service needs to write to multiple tables atomically, it creates one `Connection`, passes it to each model call, then calls `db.commit()` (or `db.rollback()` on error). Models accept `db: Connection = None` for this purpose.

### Key Business Rules

- Document validation: DNI must be exactly 8 digits; Pasaporte/Carnet must be 8–12 alphanumeric characters.
- `Caficultor` records reference a `Persona` (the person) and a `TipoCaficultor` (Socio vs. non-Socio).
- Conversion to "socio" status: `PATCH /caficultor/convertir-socio/{num_documento}`.

## Pages

| URL | Template |
|---|---|
| `/` or `/inicio` | `inicio.html` |
| `/auth/login` | `login.html` |
| `/nuevo-caficultor` | `nuevo_caficultor.html` |
| `/monitoreo` | `monitoreo.html` |
| `/registro` | `registro.html` |
