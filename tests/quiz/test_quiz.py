"""
Tests the module quizbot.quiz.quiz
"""
from quizbot.quiz.quiz import Quiz
from quizbot.quiz.question_factory import QuestionString


def test_adding_question():
    """
    Tests the initializer and the add_qustion method.
    """

    # Initialize Quiz instance
    new_quiz = Quiz("me")

    # Test list of questions, author and boolean values
    assert len(new_quiz.questions) == 0
    assert new_quiz.author == "me"
    assert new_quiz.show_results_after_question
    assert new_quiz.show_results_after_quiz
    assert not new_quiz.is_random

    # Add a new question
    new_question = QuestionString("Best Telegram bot?", "QuizBot")
    new_quiz.add_question(new_question)
    assert len(new_quiz.questions) == 1


def test_get_questions():
    """
    Tests copying the question list.
    """

    # Initialize Quiz Instance and add a new question
    new_quiz = Quiz("me")
    new_question = QuestionString("Best Telegram bot?", "QuizBot")
    new_quiz.add_question(new_question)

    # Copy list of question
    list_of_questions = new_quiz.get_questions()
    assert len(list_of_questions) == 1
