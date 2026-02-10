"""
Database connection helpers (skeleton)
This file shows how to switch between SQLite and Postgres via DATABASE_URL env var.
Replace with your project's models and real async setup (SQLAlchemy / asyncpg) when ready.
"""
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///./db.sqlite3')

if DATABASE_URL.startswith('postgres://'):
    # SQLAlchemy requires this scheme for asyncpg
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)

# Example: create an async engine here when wiring real models
# from sqlalchemy.ext.asyncio import create_async_engine
# engine = create_async_engine(DATABASE_URL, echo=True)

def get_database_url():
    return DATABASE_URL
