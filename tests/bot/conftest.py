"""
Shared fixtures and helpers for bot handler tests.
"""
import pickle
import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from quizbot.bot.models import Base, QuizModel
from quizbot.bot.persistence import SQLAlchemyPersistence
from quizbot.quiz.quiz import Quiz


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database with tables and return a sessionmaker."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session
    engine.dispose()


@pytest.fixture
def persistence(db_session):
    """Create a SQLAlchemyPersistence backed by the in-memory test database."""
    return SQLAlchemyPersistence(session_factory=db_session)


def _make_update(username="testuser", text="myquiz"):
    """Build a mocked Update with message attributes."""
    update = MagicMock()
    update.message.from_user.username = username
    update.message.text = text
    update.effective_message.chat_id = 123
    update.message.reply_text = AsyncMock()
    return update


def _make_context(session_factory, user_data=None):
    """Build a mocked context with bot_data Session and bot.send_chat_action."""
    context = MagicMock()
    context.bot_data = {"Session": session_factory}
    context.bot.send_chat_action = AsyncMock()
    context.user_data = user_data if user_data is not None else {}
    return context


def _insert_quiz(session_factory, username, quizname, quiz=None, password=None):
    """Insert a QuizModel row."""
    session = session_factory()
    if quiz is None:
        quiz = Quiz(username)
    model = QuizModel(
        username=username,
        quizname=quizname,
        quizinstance=pickle.dumps(quiz),
        password=password,
    )
    session.add(model)
    session.commit()
    session.close()
