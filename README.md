<img src="docs/_static/logo.png" height="70px" align="left" />

# QuizBot

[![Build Status](![example workflow](https://github.com/antonykamp/QuizBot/actions/workflows/test.yml/badge.svg))
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

## Attemp quiz

```python
my_attempt = Attempt(my_quiz)
```

# TOKENS

If you want to host _QuizBot_ by yourself you need some enviroment variables:

| Variable       | Usage                                     |
| -------------- | ----------------------------------------- |
| MONGODB        | The token from your MONGODB               |
| TELEGRAM_TOKEN | The token of your telegram bot            |
| WEBHOOK        | The webook to deploy the boot (eg heroku) |

If you want to test the bot you also need

| Variable    | Usage                                         |
| ----------- | --------------------------------------------- |
| API_HASH    | Your personal API_HASH to send messages       |
| API_ID      | Your personal API_ID to send messages         |
| SESSION_STR | Your personal session-string to send messages |
| UPDATER_ID  | The Updater ID to send and receive messages   |

It's no rocketscience ;)
