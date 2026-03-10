<img src="docs/_static/logo.png" height="70px" align="left" />

# QuizBot

![CI](https://github.com/antonykamp/QuizBot/actions/workflows/ci.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/quizbot/badge/?version=latest)](https://quizbot.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/antonykamp/QuizBot/branch/master/graph/badge.svg?token=8RPBQACNCW)](https://codecov.io/gh/antonykamp/QuizBot)

QuizBot is a Telegram bot with which you can create and attempt quizzes.
A quiz is a collection of possibly random questions.

The processes and conversation of creating, attempting to, renaming, and removing existing quizzes can be shown as automata-diagrams. Please take a look at the docs.

## Question types

### Multiple choice

What is **QuizBot**?

1. A Telegram bot
2. A python application
3. A city

Answer: A Telegram bot, A python application

### Single choice

What is **Quizbot**?

1. A Telegram bot
2. A dish
3. A fish

Answer: A Telegram bot

### Yes or no

Is **Quizbot** a telegram bot?

- yes
- no

Answer: yes

### Check number

In which year was **QuizBot** created?

Answer: 2020

### Check string

Where can you contribute?

Answer: Github

## Create new quiz

```python
my_quiz = Quiz()
```

## Attempt quiz

```python
my_attempt = Attempt(my_quiz)
```

## Setup

### Local development

1. Copy `.env.example` to `.env` and set `TELEGRAM_TOKEN` (get one from [@BotFather](https://t.me/BotFather))
2. Install dependencies and run migrations:
   ```bash
   uv sync --dev
   DATABASE_URL=sqlite:///dev.db uv run alembic upgrade head
   ```
3. Start the bot in polling mode:
   ```bash
   uv run python quizbot/bot/bot.py
   ```

Common scripts are also available via `hatch run`:

| Script     | Command                                            |
| ---------- | -------------------------------------------------- |
| `test`     | `hatch run test` — run the test suite              |
| `test-cov` | `hatch run test-cov` — run tests with coverage     |
| `migrate`  | `hatch run migrate` — run Alembic migrations       |
| `start`    | `hatch run start` — start the bot in polling mode  |

### Environment variables

| Variable         | Required | Description                                          |
| ---------------- | -------- | ---------------------------------------------------- |
| `TELEGRAM_TOKEN` | Yes      | Telegram bot token from @BotFather                   |
| `DATABASE_URL`   | Yes      | Database URL (e.g. `sqlite:///dev.db` for local dev) |
| `WEBHOOK`        | No       | Webhook URL for production (omit for polling mode)   |
| `PORT`           | No       | Webhook port (default: 8443)                         |

### Deployment

The bot deploys to [Render](https://render.com) via Docker. See `render.yaml` for the Blueprint configuration. Alembic migrations run automatically at container startup.
