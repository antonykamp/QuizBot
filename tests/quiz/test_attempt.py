"""
Tests the module quizbot.quiz.question_factory.
"""
from quizbot.quiz.attempt import Attempt
from quizbot.quiz.question_factory import QuestionNumber, QuestionString
from quizbot.quiz.quiz import Quiz


def test_init():
    """
    Tests if the constructor works fine.
    """
    quiz = Quiz()
    quest_a = QuestionString("What is QuizBot?", "A Telegram bot")
    quest_b = QuestionNumber("What is the best number?", "42")
    quiz.add_question(quest_a)
    quiz.add_question(quest_b)
    quiz.is_random = True
    att = Attempt(quiz)

    assert att.quiz == quiz
    assert set(att.questions) == set(quiz.questions)


def test_question_answer():
    """
    Tests if the process of entering a answer works fine.
    """
    quiz = Quiz()
    quest = QuestionString("What is QuizBot?", "A Telegram bot")
    quiz.add_question(quest)
    att = Attempt(quiz)

    assert att.has_next_question()
    assert att.act_question() == quest
    att.input_answer("A Telegram bot")
    assert att.enter_answer()[0]
    assert not att.has_next_question()
    assert att.user_points[0][0]
