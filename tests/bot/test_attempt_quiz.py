"""
Tests the quiz attempt flow in quizbot.bot.attempt_quiz.
"""
import pytest
from unittest.mock import MagicMock

from telegram.ext import ConversationHandler

from argon2 import PasswordHasher
from quizbot.bot.attempt_quiz import start, cancel, enter_quiz, enter_answer, enter_password
from quizbot.quiz.quiz import Quiz
from quizbot.quiz.attempt import Attempt
from quizbot.quiz.question_factory import QuestionString, QuestionChoice
from tests.bot.conftest import _make_update, _make_context, _insert_quiz


# -- start tests --

@pytest.mark.asyncio
async def test_start_returns_enter_quiz():
    update = _make_update()
    context = _make_context(MagicMock())

    result = await start(update, context)

    assert result == "ENTER_QUIZ"
    update.message.reply_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_rejects_double_attempt():
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("Q?", "A"))
    attempt = Attempt(quiz)
    update = _make_update()
    context = _make_context(MagicMock(), user_data={"attempt": attempt})

    result = await start(update, context)

    assert result == ConversationHandler.END
    reply_text = update.message.reply_text.call_args[0][0]
    assert "middle of a quiz" in reply_text.lower()


# -- cancel tests --

@pytest.mark.asyncio
async def test_cancel_clears_user_data():
    update = _make_update()
    context = _make_context(MagicMock(), user_data={"attempt": "dummy"})

    result = await cancel(update, context)

    assert result == ConversationHandler.END
    assert context.user_data == {}


# -- enter_quiz tests --

@pytest.mark.asyncio
async def test_enter_quiz_found(db_session):
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))
    _insert_quiz(db_session, "testuser", "myquiz", quiz=quiz)

    update = _make_update(username="testuser", text="myquiz")
    context = _make_context(db_session)

    result = await enter_quiz(update, context)

    assert result == "ENTER_ANSWER"
    assert isinstance(context.user_data["attempt"], Attempt)
    assert len(context.user_data["attempt"].questions) == 1


@pytest.mark.asyncio
async def test_enter_quiz_not_found(db_session):
    update = _make_update(username="testuser", text="no_such_quiz")
    context = _make_context(db_session)

    result = await enter_quiz(update, context)

    assert result == "ENTER_QUIZ"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "couldn't find" in reply_text.lower()


@pytest.mark.asyncio
async def test_enter_quiz_with_creator_name(db_session):
    quiz = Quiz("creator")
    quiz.add_question(QuestionString("What?", "answer"))
    _insert_quiz(db_session, "creator", "myquiz", quiz=quiz)

    update = _make_update(username="otheruser", text="myquiz creator")
    context = _make_context(db_session)

    result = await enter_quiz(update, context)

    assert result == "ENTER_ANSWER"
    assert isinstance(context.user_data["attempt"], Attempt)


# -- enter_answer tests --

@pytest.mark.asyncio
async def test_enter_answer_correct():
    quiz = Quiz("testuser")
    quiz.show_results_after_question = True
    quiz.show_results_after_quiz = False
    quiz.add_question(QuestionString("What?", "answer"))
    quiz.add_question(QuestionString("Q2?", "a2"))
    attempt = Attempt(quiz)

    update = _make_update(text="answer")
    context = _make_context(MagicMock(), user_data={"attempt": attempt})

    result = await enter_answer(update, context)

    assert result == "ENTER_ANSWER"
    # Should report correct
    calls = [c[0][0] for c in update.message.reply_text.call_args_list]
    assert any("correct" in c.lower() for c in calls)


@pytest.mark.asyncio
async def test_enter_answer_wrong():
    quiz = Quiz("testuser")
    quiz.show_results_after_question = True
    quiz.show_results_after_quiz = False
    quiz.add_question(QuestionString("What?", "answer"))
    quiz.add_question(QuestionString("Q2?", "a2"))
    attempt = Attempt(quiz)

    update = _make_update(text="wrong")
    context = _make_context(MagicMock(), user_data={"attempt": attempt})

    result = await enter_answer(update, context)

    assert result == "ENTER_ANSWER"
    calls = [c[0][0] for c in update.message.reply_text.call_args_list]
    assert any("not correct" in c.lower() for c in calls)


@pytest.mark.asyncio
async def test_enter_answer_last_question_ends():
    quiz = Quiz("testuser")
    quiz.show_results_after_question = False
    quiz.show_results_after_quiz = False
    quiz.add_question(QuestionString("What?", "answer"))
    attempt = Attempt(quiz)

    update = _make_update(text="answer")
    context = _make_context(MagicMock(), user_data={"attempt": attempt})

    result = await enter_answer(update, context)

    assert result == ConversationHandler.END
    assert context.user_data == {}


@pytest.mark.asyncio
async def test_enter_answer_multiple_choice_waits_for_enter():
    quiz = Quiz("testuser")
    quiz.show_results_after_question = False
    quiz.show_results_after_quiz = False
    q = QuestionChoice("Pick all", "a, b")
    q.add_possible_answer("c")
    quiz.add_question(q)
    attempt = Attempt(quiz)

    update = _make_update(text="a")
    context = _make_context(MagicMock(), user_data={"attempt": attempt})

    result = await enter_answer(update, context)

    assert result == "ENTER_ANSWER"
    # Question should still be active (not entered yet)
    assert attempt.has_next_question()


# -- password-protected quiz tests --

@pytest.mark.asyncio
async def test_enter_quiz_password_protected_asks_for_password(db_session):
    ph = PasswordHasher()
    hashed = ph.hash("secret")
    quiz = Quiz("creator")
    quiz.add_question(QuestionString("What?", "answer"))
    _insert_quiz(db_session, "creator", "locked_quiz", quiz=quiz, password=hashed)

    update = _make_update(username="otheruser", text="locked_quiz creator")
    context = _make_context(db_session)

    result = await enter_quiz(update, context)

    assert result == "ENTER_PASSWORD"
    assert "pending_quiz" in context.user_data
    assert "pending_password" in context.user_data
    reply_text = update.message.reply_text.call_args[0][0]
    assert "password" in reply_text.lower()


@pytest.mark.asyncio
async def test_enter_quiz_author_bypasses_password(db_session):
    ph = PasswordHasher()
    hashed = ph.hash("secret")
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))
    _insert_quiz(db_session, "testuser", "locked_quiz", quiz=quiz, password=hashed)

    update = _make_update(username="testuser", text="locked_quiz")
    context = _make_context(db_session)

    result = await enter_quiz(update, context)

    assert result == "ENTER_ANSWER"
    assert isinstance(context.user_data["attempt"], Attempt)


@pytest.mark.asyncio
async def test_enter_password_correct_starts_quiz(db_session):
    ph = PasswordHasher()
    hashed = ph.hash("secret")
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))

    update = _make_update(text="secret")
    context = _make_context(db_session, user_data={
        "pending_quiz": quiz,
        "pending_password": hashed,
        "pending_quizname": "locked_quiz",
    })

    result = await enter_password(update, context)

    assert result == "ENTER_ANSWER"
    assert isinstance(context.user_data["attempt"], Attempt)
    assert "pending_quiz" not in context.user_data


@pytest.mark.asyncio
async def test_enter_password_wrong_reprompts(db_session):
    ph = PasswordHasher()
    hashed = ph.hash("secret")
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))

    update = _make_update(text="wrongpassword")
    context = _make_context(db_session, user_data={
        "pending_quiz": quiz,
        "pending_password": hashed,
        "pending_quizname": "locked_quiz",
    })

    result = await enter_password(update, context)

    assert result == "ENTER_PASSWORD"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "wrong password" in reply_text.lower()
