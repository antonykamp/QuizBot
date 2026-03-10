# Contributing to QuizBot

Thanks for your interest in contributing! Here's how to get started.

## Setup

1. Fork and clone the repository
2. Copy `.env.example` to `.env` and set `TELEGRAM_TOKEN`
3. Install dependencies:
   ```bash
   uv sync --dev
   ```
4. Run migrations:
   ```bash
   DATABASE_URL=sqlite:///dev.db uv run alembic upgrade head
   ```
5. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Development workflow

1. Create a branch from `master`
2. Make your changes
3. Run the tests:
   ```bash
   uv run pytest tests/
   ```
4. Push your branch and open a pull request

## Project structure

- `quizbot/quiz/` — Domain models (no Telegram dependency)
- `quizbot/bot/` — Telegram conversation handlers
- `tests/quiz/` — Domain model tests
- `tests/bot/` — Bot handler tests
- `docs/` — Sphinx documentation

## Guidelines

- Keep PRs focused on a single change
- Add tests for new functionality
- Run `ruff check` before committing (pre-commit hooks do this automatically)
- Bot handler tests use an in-memory SQLite database — see `tests/bot/conftest.py` for shared fixtures

## Reporting issues

Use the [GitHub issue templates](https://github.com/antonykamp/QuizBot/issues/new/choose) for bugs, feature requests, or questions.
