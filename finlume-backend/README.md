# Finlume Backend

A standalone FastAPI backend service for the Finlume AI companion app.

## Features

- **FastAPI Framework**: High performance, easy to build API routes.
- **SQLAlchemy ORM**: Configured for PostgreSQL database interactions.
- **Alembic**: Database migrations configured and ready.
- **Authentication**: JWT-based authentication with `bcrypt` password hashing.
- **Configuration Management**: Handles dynamic environment variables using `pydantic-settings` from a `.env` file.
- **CORS Enabled**: Configured to work with frontend clients running on port `5173`.
- **Health Check**: Dynamic health monitoring endpoint.

## Project Structure

```text
finlume-backend/
├── alembic/              # Database migration configurations and files
├── app/                  # Application core code
│   ├── core/             # Configuration, security utilities, and constants
│   │   ├── config.py     # Pydantic Settings loaders
│   │   └── security.py   # JWT & Password helper functions
│   ├── database.py       # SQLAlchemy engine & session dependency
│   └── main.py           # FastAPI entrypoint, middleware, and core routing
├── .env                  # Local environment file (ignored from git)
├── .env.example          # Sample environment variables template
├── .gitignore            # Standard git exclusion lists
├── README.md             # This documentation
└── requirements.txt      # Python package dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database instance running

### Installation

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```powershell
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure local environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Update `.env` with your actual Postgres details, JWT secret, and Anthropic API keys.)*

### Database Migrations

To generate a new database migration:
```bash
alembic revision --autogenerate -m "Initial schema"
```

To run all pending migrations:
```bash
alembic upgrade head
```

### Running the Server

Start the local development server using Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
The interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).
