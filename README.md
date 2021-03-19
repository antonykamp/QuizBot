# QuizBot

[![Coverage Status](https://coveralls.io/repos/github/DuckNrOne/QuizBot/badge.svg?branch=main&t=DI7SAu)](https://coveralls.io/github/DuckNrOne/QuizBot?branch=main)

QuizBot is a Telegram bot with which you can create and attempt quizzes.
A quiz is a collection of possibly random questions.

The processes and conversation of creating, attempting to, renaming, and removing existing  quizzes can be shown as automata-diagrams. Please take a look at the docs.

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

It's no rocketscience
