Question types
==============

You can use different kinds of questions in your quizzes.
But you are free to add more by creating a subclass of `Question`.
Here are the types which already exist.

Multiple choice: `QuestionChoice`
--------------------------------

What is **QuizBot**?

1. A Telegram bot
2. A python application
3. A city

Answer: A Telegram bot, A python application

.. code-block:: python

  my_question = QuestionChoice("What is QuizBot?", "A Telegram bot, A python application")
  my_question.add_possible_answer("A city")


Single choice: `QuestionChoiceSingle`
-------------------------------------
What is **Quizbot**?

1. A Telegram bot
2. A dish
3. A fish

Answer: A Telegram bot

.. code-block:: python

    my_question = QuestionChoiceSingle("What is QuizBot?", "A Telegram bot")
    my_question.add_possible_answer("A dish")
    my_question.add_possible_answer("A fish")

Yes or no : `QuestionBool`
--------------------------

Is **Quizbot** a telegram bot?

- yes
- no

Answer: yes

.. code-block:: python

    my_question = QuestionBool("What is QuizBot?", "Yes")

Check number: `QuestionNumber`
------------------------------

In which year was **QuizBot** created?

Answer: 2020

.. code-block:: python

    my_question = QuestionNumber("In which year was QuizBot created?", "2020")

Check string: `QuestionString`
------------------------------

Where can you contribute?

Answer: Github

.. code-block:: python

    my_question = QuestionString("Where can you contribute?", "Github")