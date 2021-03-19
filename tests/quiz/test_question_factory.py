"""
Tests the module quizbot.quiz.question_factory.
"""
import pytest
from quizbot.quiz.question_factory import QuestionNumber, QuestionString, \
    QuestionBool, QuestionChoice, QuestionChoiceSingle


def test_question_number():
    """
    Tests the general functions of the question class with an instance of the question_number class.
    """

    # Initialize a test instance of question_number
    question = QuestionNumber("Best number of the world?", "42")

    # checks entered values
    assert question.correct_answer == "42"
    assert question.question == "Best number of the world?"

    # exception for checking solution without entering user answer
    with pytest.raises(AssertionError):
        question.check_solution()

    # exception for entering no number
    with pytest.raises(AssertionError):
        question.enter_solution("wrong enter")

    # Check wrong user answer
    question.enter_solution("23")
    assert question.user_answer == "23"
    assert not question.check_solution()

    # Check correct user answer
    question.enter_solution("42")
    assert question.check_solution()


def test_question_string():
    """
    Tests instances of the question_strings class.
    """

    # Initialize a test instance of question_number
    question = QuestionString("Best project on github?", "QuizBot")

    # Check wrong user answer
    question.enter_solution("LameStuff")
    assert not question.check_solution()

    # Check correct user answer
    question.enter_solution("QuizBot")
    assert question.check_solution()


def test_question_bool():
    """
    Tests instances of the question_bool class.
    """

    # Initialize a test instance of question_number
    question = QuestionBool("Is QuizBot great?", "True")

    # Exception for entering no boolean value
    with pytest.raises(AssertionError):
        question.enter_solution("wrong enter")

    # Check correct user answer
    question.enter_solution("True")
    assert question.check_solution()


def test_question_choice():
    """
    Tests instances of the question_choice class.
    """

    # Exception for entering no correct answer
    with pytest.raises(AssertionError):
        QuestionChoice("What is QuizBot?", "")

    # Initialize a test instance of question_number
    question = QuestionChoice(
        "What is QuizBot?", "A python application, A Telegram bot")

    # Check setting random order
    assert not question.is_random
    question.is_random = True
    assert question.is_random

    # Check the list of possible answers
    assert isinstance(question.possible_answers, list)
    assert len(question.possible_answers) == 2
    question.add_possible_answer("A city")
    assert len(question.possible_answers) == 3

    # Check correct entered user answer
    question.enter_solution("A city, A python application")
    assert not question.check_solution()
    question.enter_solution("A Telegram bot, A python application")
    assert question.check_solution()


def test_question_choice_single():
    """
    Tests instances of the question_choice_single class.
    """
    # Exception for entering empty string as correct answer
    with pytest.raises(AssertionError):
        QuestionChoiceSingle("What is QuizBot?", "")

    # Initialize a test instance of question_number
    question = QuestionChoiceSingle("What is QuizBot?", "A Telegram bot")

    # Add possible answers
    question.add_possible_answer("A dish")
    question.add_possible_answer("A fish")

    # Exception for entering multiple answers by user
    with pytest.raises(AssertionError):
        question.enter_solution("A dish, A fish")

    # Check correct entered user answer
    question.enter_solution("A Telegram bot")
    assert question.check_solution()
