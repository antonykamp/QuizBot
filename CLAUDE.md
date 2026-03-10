# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuizBot is a Telegram bot for creating and taking quizzes, built with `python-telegram-bot` (v21.x, async) and PostgreSQL with SQLAlchemy for persistence. Deployed via Docker.

## Commands

### Install dependencies
```bash
uv sync --dev
```

### Run tests
```bash
uv run pytest tests/
```

### Run tests with coverage
```bash
uv run pytest --cov-report=xml --cov=quizbot tests/
```

### Run a single test file
```bash
uv run pytest tests/quiz/test_quiz.py
```

### Run migrations (local development)
```bash
DATABASE_URL=sqlite:///dev.db uv run alembic upgrade head
```

### Generate a new migration after model changes
```bash
DATABASE_URL=sqlite:///dev.db uv run alembic revision --autogenerate -m "describe change"
```

Production migrations run automatically at container startup via the Dockerfile CMD before the bot starts.

### Build Docker image
```bash
docker build -t quizbot .
```

### Build documentation (Sphinx)
```bash
cd docs && make html
```

### Run the bot locally (polling mode)
Copy `.env.example` to `.env`, set `TELEGRAM_TOKEN`, and run:
```bash
uv run python quizbot/bot/bot.py
```
When `WEBHOOK` is unset the bot starts in polling mode with a local SQLite database (`dev.db`). Set `WEBHOOK` to use webhook mode (production).

## Architecture

Two-layer design separating Telegram bot handlers from domain logic:

- **`quizbot/quiz/`** — Domain models (no Telegram dependency):
  - `quiz.py`: Quiz container holding questions with display/randomization settings
  - `attempt.py`: Tracks user progress through a quiz, manages scoring and question ordering
  - `question_factory.py`: Polymorphic question hierarchy (`QuestionNumber`, `QuestionString`, `QuestionBool`, `QuestionChoice`, `QuestionChoiceSingle`) with a factory for instantiation

- **`quizbot/bot/`** — Telegram conversation handlers (async, python-telegram-bot v21):
  - `models.py`: SQLAlchemy model (`QuizModel`) mapping quizzes to a PostgreSQL table with `username`, `quizname`, and `quizinstance` columns
  - `config.py`: Centralized configuration — validates required env vars (`TELEGRAM_TOKEN`, `DATABASE_URL`) at startup and creates a SQLAlchemy `sessionmaker`. `WEBHOOK` is optional (omit for polling mode). Schema management is handled by Alembic migrations (see `migrations/`), not `create_all`
  - `bot.py`: Entry point, registers all `ConversationHandler`s and starts in webhook or polling mode via `ApplicationBuilder`. Stores the shared `Session` factory on `app.bot_data['Session']`
  - `create_quiz.py`: Multi-step quiz creation flow (question type -> question -> answer -> settings -> name), stores to PostgreSQL
  - `attempt_quiz.py`: Quiz attempt flow, retrieves from PostgreSQL, tracks answers
  - `edit_quiz.py`: Rename/delete quiz operations

Bot handlers use `telegram.ext.ConversationHandler` with defined states for multi-step interactions. All handlers are `async def` and use `await` for Telegram API calls. User session data is held in `context.user_data` during conversations. The database session factory is accessed via `context.bot_data['Session']`. Blocking SQLAlchemy calls are wrapped in `asyncio.to_thread()`. Completed quizzes persist in PostgreSQL.

## Testing

Tests live in `tests/quiz/` and cover domain models only (no bot handler tests). Uses pytest.
