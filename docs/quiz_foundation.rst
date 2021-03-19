Quiz Foundation
===============
With the *Quiz Foundation* you can...
- ... create Quizzes with `quiz.quiz.py`
- ... create Questions of different kinds with `quiz.question_factory.py`
- ... attempt quizzes with `quiz.attempt.py`.

Lets get threw the process.

1. Init a quiz
---------------
With the class `Quiz` in `quiz.quiz.py`, you create a new quiz by creating a new Quiz-object.
You can specify an author by entering the authors' name by argument. Otherwise, the author is an empty string.

.. code-block:: python

    my_quiz = Quiz("my_name")


Before you can add a question to the quiz you have to create one.

2. Create a question
---------------------
You can create a new question by using one of the subclasses of `Question` in `quiz.question_factory.py`.
You have to pass two arguments by the creator:
- the question itself as a string
- the correct answer(s separated by a ',' if it's a multiple-choice question) as a string.

Whatever kind of question you choose, the program checks if the entered answer is convertible to the wanted format.
In this case, you just want to ask for a string.

.. code-block:: python

 >>> my_question = QuestionString("What's the best project?", "QuizBot")


Now we want to add this question to our quiz.

3. Add a question to quiz
-------------------------
We can add an instance of the class `Question` simply by calling `my_quiz.add_question`.

.. code-block:: python

    >>> my_quiz.add_question(my_question)


If we'd want to add more questions to the quiz, we would create a new question and add it.
Otherwise, we could specify if we want to print questions in random order (and more stuff ;).
At the moment we don't want to do more. But we want to attempt it.

4. Attempt to quiz
------------------
We can attempt to a quiz by passing it to the constructor of the `Attempt` class in `quiz.attempt.py`.

.. code-block:: python

    >>> my_attempt = Attempt(my_quiz)


Now we can if it has a question left with `has_next_question`. 
In that case, we can ask for the question itself with `act_question`.
If we know the answer to the question, we pass it by `input_answer` as a string and call `enter_answer` to enter it.
You can check whether you were right or not by checking the return value of `enter_answer`.

.. code-block:: python

    >>> print(my_attempt.has_next_question())
    true
    >>> print(my_attempt.act_question)
    "What's the best project?"
    >>> act_question.input_answer("QuizBot")
    >>> print(act_question.enter_answer())
    true
    >>> print(my_attempt.has_next_question())
    false


Because we don't have questions left, we can check the result of every question in `my_attempt.user_points`.
That's it...it's not rocket science ;)