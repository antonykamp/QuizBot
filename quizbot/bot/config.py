"""
Centralized configuration and database connection for QuizBot.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parents[2] / '.env')


def get_config():
    """Load and validate all required configuration from environment variables."""
    required = {
        'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN'),
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
    return {
        **required,
        'WEBHOOK': os.environ.get('WEBHOOK'),
        'PORT': int(os.environ.get('PORT', '8443')),
    }


def get_session_factory(database_url):
    """Create a SQLAlchemy engine and return a sessionmaker."""
    engine = create_engine(database_url)
    return sessionmaker(bind=engine)
