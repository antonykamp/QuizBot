"""
Tests the quiz creation flow in quizbot.bot.create_quiz.
"""
import pytest
from unittest.mock import MagicMock

from telegram.ext import ConversationHandler

from quizbot.bot.create_quiz import (
    start, cancel, enter_type, enter_question, enter_answer,
    enter_possible_answer, enter_randomness_question,
    enter_randomness_quiz, enter_result_after_question,
    enter_result_after_quiz, enter_quiz_name,
    enter_password_choice, enter_password,
)
from quizbot.bot.models import QuizModel
from quizbot.quiz.quiz import Quiz
from quizbot.quiz.question_factory import (
    QuestionString, QuestionNumber, QuestionChoice, QuestionChoiceSingle,
)
from tests.bot.conftest import _make_update, _make_context, _insert_quiz


# -- start tests --

@pytest.mark.asyncio
async def test_start_creates_quiz_in_user_data():
    update = _make_update(username="creator")
    context = _make_context(MagicMock())

    result = await start(update, context)

    assert result == "ENTER_TYPE"
    assert isinstance(context.user_data["quiz"], Quiz)
    assert context.user_data["quiz"].author == "creator"


@pytest.mark.asyncio
async def test_start_rejects_double_creation():
    update = _make_update()
    context = _make_context(MagicMock(), user_data={"quiz": Quiz("testuser")})

    result = await start(update, context)

    assert result == ConversationHandler.END
    reply_text = update.message.reply_text.call_args[0][0]
    assert "middle of a creation" in reply_text.lower()


# -- cancel tests --

@pytest.mark.asyncio
async def test_cancel_clears_user_data():
    update = _make_update()
    context = _make_context(MagicMock(), user_data={"quiz": Quiz("testuser")})

    result = await cancel(update, context)

    assert result == ConversationHandler.END
    assert context.user_data == {}


# -- enter_type tests --

@pytest.mark.asyncio
async def test_enter_type_saves_question_type_string():
    update = _make_update(text="Ask for a string")
    context = _make_context(MagicMock(), user_data={"quiz": Quiz("testuser")})

    result = await enter_type(update, context)

    assert result == "ENTER_QUESTION"
    assert context.user_data["questtype"] is QuestionString


@pytest.mark.asyncio
async def test_enter_type_saves_question_type_number():
    update = _make_update(text="Ask for a number")
    context = _make_context(MagicMock(), user_data={"quiz": Quiz("testuser")})

    result = await enter_type(update, context)

    assert result == "ENTER_QUESTION"
    assert context.user_data["questtype"] is QuestionNumber


@pytest.mark.asyncio
async def test_enter_type_enter_finishes_questions():
    update = _make_update(text="Enter")
    context = _make_context(MagicMock(), user_data={"quiz": Quiz("testuser")})

    result = await enter_type(update, context)

    assert result == "ENTER_RANDOMNESS_QUIZ"


# -- enter_question tests --

@pytest.mark.asyncio
async def test_enter_question_saves_question_text():
    update = _make_update(text="What is 2+2?")
    context = _make_context(
        MagicMock(),
        user_data={"quiz": Quiz("testuser"), "questtype": QuestionString},
    )

    result = await enter_question(update, context)

    assert result == "ENTER_ANSWER"
    assert context.user_data["question"] == "What is 2+2?"


# -- enter_answer tests --

@pytest.mark.asyncio
async def test_enter_answer_valid_string():
    update = _make_update(text="four")
    context = _make_context(
        MagicMock(),
        user_data={
            "quiz": Quiz("testuser"),
            "questtype": QuestionString,
            "question": "What is 2+2?",
        },
    )

    result = await enter_answer(update, context)

    assert result == "ENTER_TYPE"
    assert len(context.user_data["quiz"].questions) == 1
    assert isinstance(context.user_data["quiz"].questions[0], QuestionString)


@pytest.mark.asyncio
async def test_enter_answer_choice_goes_to_possible_answers():
    update = _make_update(text="correct1, correct2")
    context = _make_context(
        MagicMock(),
        user_data={
            "quiz": Quiz("testuser"),
            "questtype": QuestionChoice,
            "question": "Pick all that apply",
        },
    )

    result = await enter_answer(update, context)

    assert result == "ENTER_POSSIBLE_ANSWER"
    assert isinstance(context.user_data["questionInstance"], QuestionChoice)


@pytest.mark.asyncio
async def test_enter_answer_single_choice_goes_to_possible_answers():
    update = _make_update(text="correct")
    context = _make_context(
        MagicMock(),
        user_data={
            "quiz": Quiz("testuser"),
            "questtype": QuestionChoiceSingle,
            "question": "Pick one",
        },
    )

    result = await enter_answer(update, context)

    assert result == "ENTER_POSSIBLE_ANSWER"
    assert isinstance(context.user_data["questionInstance"], QuestionChoiceSingle)


# -- enter_possible_answer tests --

@pytest.mark.asyncio
async def test_enter_possible_answer_adds_answers():
    question = QuestionChoice("Pick all", "correct")
    update = _make_update(text="wrong1, wrong2")
    context = _make_context(
        MagicMock(),
        user_data={"quiz": Quiz("testuser"), "questionInstance": question},
    )

    result = await enter_possible_answer(update, context)

    assert result == "ENTER_RANDOMNESS_QUESTION"
    assert "wrong1" in question.possible_answers
    assert "wrong2" in question.possible_answers


# -- enter_randomness_question tests --

@pytest.mark.asyncio
async def test_enter_randomness_question_yes():
    question = QuestionChoice("Pick all", "correct")
    quiz = Quiz("testuser")
    update = _make_update(text="Yes")
    context = _make_context(
        MagicMock(),
        user_data={"quiz": quiz, "questionInstance": question},
    )

    result = await enter_randomness_question(update, context)

    assert result == "ENTER_TYPE"
    assert question.is_random is True
    assert len(quiz.questions) == 1


@pytest.mark.asyncio
async def test_enter_randomness_question_no():
    question = QuestionChoice("Pick all", "correct")
    quiz = Quiz("testuser")
    update = _make_update(text="No")
    context = _make_context(
        MagicMock(),
        user_data={"quiz": quiz, "questionInstance": question},
    )

    result = await enter_randomness_question(update, context)

    assert result == "ENTER_TYPE"
    assert question.is_random is False


@pytest.mark.asyncio
async def test_enter_randomness_question_invalid_input():
    question = QuestionChoice("Pick all", "correct")
    update = _make_update(text="maybe")
    context = _make_context(
        MagicMock(),
        user_data={"quiz": Quiz("testuser"), "questionInstance": question},
    )

    result = await enter_randomness_question(update, context)

    assert result == "ENTER_RANDOMNESS_QUESTION"


# -- enter_randomness_quiz tests --

@pytest.mark.asyncio
async def test_enter_randomness_quiz_yes():
    quiz = Quiz("testuser")
    update = _make_update(text="Yes")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_randomness_quiz(update, context)

    assert result == "ENTER_RESULT_AFTER_QUESTION"
    assert quiz.is_random is True


@pytest.mark.asyncio
async def test_enter_randomness_quiz_no():
    quiz = Quiz("testuser")
    update = _make_update(text="No")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_randomness_quiz(update, context)

    assert result == "ENTER_RESULT_AFTER_QUESTION"
    assert quiz.is_random is False


@pytest.mark.asyncio
async def test_enter_randomness_quiz_invalid_reprompts():
    quiz = Quiz("testuser")
    update = _make_update(text="maybe")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_randomness_quiz(update, context)

    assert result == "ENTER_RANDOMNESS_QUIZ"


# -- enter_result_after_question tests --

@pytest.mark.asyncio
async def test_enter_result_after_question_yes():
    quiz = Quiz("testuser")
    update = _make_update(text="Yes")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_result_after_question(update, context)

    assert result == "ENTER_RESULT_AFTER_QUIZ"
    assert quiz.show_results_after_question is True


@pytest.mark.asyncio
async def test_enter_result_after_question_no():
    quiz = Quiz("testuser")
    update = _make_update(text="No")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_result_after_question(update, context)

    assert result == "ENTER_RESULT_AFTER_QUIZ"
    assert quiz.show_results_after_question is False


@pytest.mark.asyncio
async def test_enter_result_after_question_invalid_reprompts():
    quiz = Quiz("testuser")
    update = _make_update(text="dunno")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_result_after_question(update, context)

    assert result == "ENTER_RESULT_AFTER_QUESTION"


# -- enter_result_after_quiz tests --

@pytest.mark.asyncio
async def test_enter_result_after_quiz_yes():
    quiz = Quiz("testuser")
    update = _make_update(text="Yes")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_result_after_quiz(update, context)

    assert result == "ENTER_QUIZ_NAME"
    assert quiz.show_results_after_quiz is True


@pytest.mark.asyncio
async def test_enter_result_after_quiz_no():
    quiz = Quiz("testuser")
    update = _make_update(text="No")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_result_after_quiz(update, context)

    assert result == "ENTER_QUIZ_NAME"
    assert quiz.show_results_after_quiz is False


@pytest.mark.asyncio
async def test_enter_result_after_quiz_invalid_reprompts():
    quiz = Quiz("testuser")
    update = _make_update(text="nah")
    context = _make_context(MagicMock(), user_data={"quiz": quiz})

    result = await enter_result_after_quiz(update, context)

    assert result == "ENTER_RESULT_AFTER_QUIZ"


# -- enter_quiz_name tests --

@pytest.mark.asyncio
async def test_enter_quiz_name_goes_to_password_choice(db_session):
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))
    update = _make_update(username="testuser", text="my_new_quiz")
    context = _make_context(db_session, user_data={"quiz": quiz})

    result = await enter_quiz_name(update, context)

    assert result == "ENTER_PASSWORD_CHOICE"
    assert context.user_data["quizname"] == "my_new_quiz"


@pytest.mark.asyncio
async def test_enter_quiz_name_duplicate(db_session):
    _insert_quiz(db_session, "testuser", "existing_quiz")
    quiz = Quiz("testuser")
    update = _make_update(username="testuser", text="existing_quiz")
    context = _make_context(db_session, user_data={"quiz": quiz})

    result = await enter_quiz_name(update, context)

    assert result == "ENTER_QUIZ_NAME"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "already" in reply_text.lower()


# -- enter_password_choice tests --

@pytest.mark.asyncio
async def test_enter_password_choice_no_saves_without_password(db_session):
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))
    update = _make_update(username="testuser", text="No")
    context = _make_context(db_session, user_data={"quiz": quiz, "quizname": "my_quiz"})

    result = await enter_password_choice(update, context)

    assert result == ConversationHandler.END
    assert context.user_data == {}

    session = db_session()
    row = session.query(QuizModel).filter_by(username="testuser", quizname="my_quiz").first()
    session.close()
    assert row is not None
    assert row.password is None


@pytest.mark.asyncio
async def test_enter_password_choice_yes(db_session):
    quiz = Quiz("testuser")
    update = _make_update(text="Yes")
    context = _make_context(db_session, user_data={"quiz": quiz, "quizname": "my_quiz"})

    result = await enter_password_choice(update, context)

    assert result == "ENTER_PASSWORD"


@pytest.mark.asyncio
async def test_enter_password_choice_invalid_reprompts(db_session):
    quiz = Quiz("testuser")
    update = _make_update(text="maybe")
    context = _make_context(db_session, user_data={"quiz": quiz, "quizname": "my_quiz"})

    result = await enter_password_choice(update, context)

    assert result == "ENTER_PASSWORD_CHOICE"


# -- enter_password tests --

@pytest.mark.asyncio
async def test_enter_password_saves_with_hashed_password(db_session):
    quiz = Quiz("testuser")
    quiz.add_question(QuestionString("What?", "answer"))
    update = _make_update(username="testuser", text="secret123")
    context = _make_context(db_session, user_data={"quiz": quiz, "quizname": "my_quiz"})

    result = await enter_password(update, context)

    assert result == ConversationHandler.END
    assert context.user_data == {}

    session = db_session()
    row = session.query(QuizModel).filter_by(username="testuser", quizname="my_quiz").first()
    session.close()
    assert row is not None
    assert row.password is not None
    assert row.password.startswith("$argon2")
