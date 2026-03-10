"""
Centralized configuration and database connection for QuizBot.
"""

import os

import pymongo


def get_config():
    """Load and validate all required configuration from environment variables."""
    required = {
        'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN'),
        'WEBHOOK': os.environ.get('WEBHOOK'),
        'MONGODB': os.environ.get('MONGODB'),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
    return {
        **required,
        'PORT': int(os.environ.get('PORT', '8443')),
    }


def get_db(mongodb_uri):
    """Create a MongoDB client and return the quizzes database."""
    return pymongo.MongoClient(mongodb_uri).quizzes
