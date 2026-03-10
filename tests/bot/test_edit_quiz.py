"""
Tests the delete (remove) and rename flows in quizbot.bot.edit_quiz.
"""
import pytest
from unittest.mock import MagicMock

from telegram.ext import ConversationHandler

from quizbot.bot.models import QuizModel
from quizbot.bot.edit_quiz import (
    start_remove, enter_name_remove, cancel_edit,
    start_rename, enter_old_name, enter_new_name,
)
from tests.bot.conftest import _make_update, _make_context, _insert_quiz


# -- start_remove tests --

@pytest.mark.asyncio
async def test_start_remove_replies_and_returns_enter_name():
    update = _make_update()
    result = await start_remove(update, None)

    update.message.reply_text.assert_awaited_once()
    assert "delete" in update.message.reply_text.call_args[0][0].lower()
    assert result == "ENTER_NAME"


# -- enter_name_remove tests --

@pytest.mark.asyncio
async def test_enter_name_remove_deletes_existing_quiz(db_session):
    _insert_quiz(db_session, "testuser", "myquiz")

    update = _make_update(username="testuser", text="myquiz")
    context = _make_context(db_session)

    result = await enter_name_remove(update, context)

    assert result == ConversationHandler.END
    reply_text = update.message.reply_text.call_args[0][0]
    assert "deleted" in reply_text.lower()
    assert "myquiz" in reply_text

    # Verify the quiz is actually gone from the database
    session = db_session()
    remaining = session.query(QuizModel).filter_by(username="testuser", quizname="myquiz").first()
    session.close()
    assert remaining is None


@pytest.mark.asyncio
async def test_enter_name_remove_nonexistent_quiz(db_session):
    update = _make_update(username="testuser", text="no_such_quiz")
    context = _make_context(db_session)

    result = await enter_name_remove(update, context)

    assert result == "ENTER_NAME"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "doesn't exist" in reply_text
    assert "no_such_quiz" in reply_text


@pytest.mark.asyncio
async def test_enter_name_remove_wrong_user_cannot_delete(db_session):
    _insert_quiz(db_session, "owner", "myquiz")

    update = _make_update(username="other_user", text="myquiz")
    context = _make_context(db_session)

    result = await enter_name_remove(update, context)

    assert result == "ENTER_NAME"

    # Quiz still exists for the original owner
    session = db_session()
    remaining = session.query(QuizModel).filter_by(username="owner", quizname="myquiz").first()
    session.close()
    assert remaining is not None


# -- cancel_edit tests --

@pytest.mark.asyncio
async def test_cancel_edit_returns_end():
    update = _make_update()
    context = _make_context(MagicMock())

    result = await cancel_edit(update, context)

    assert result == ConversationHandler.END
    update.message.reply_text.assert_awaited_once()
    assert "canceled" in update.message.reply_text.call_args[0][0].lower()


# -- start_rename tests --

@pytest.mark.asyncio
async def test_start_rename_replies_and_returns_enter_old_name():
    update = _make_update()
    result = await start_rename(update, None)

    update.message.reply_text.assert_awaited_once()
    assert "rename" in update.message.reply_text.call_args[0][0].lower()
    assert result == "ENTER_OLD_NAME"


# -- enter_old_name tests --

@pytest.mark.asyncio
async def test_enter_old_name_existing_quiz(db_session):
    _insert_quiz(db_session, "testuser", "myquiz")

    update = _make_update(username="testuser", text="myquiz")
    context = _make_context(db_session)

    result = await enter_old_name(update, context)

    assert result == "ENTER_NEW_NAME"
    assert context.user_data["old_quiz_name"] == "myquiz"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "name" in reply_text.lower()


@pytest.mark.asyncio
async def test_enter_old_name_nonexistent_quiz(db_session):
    update = _make_update(username="testuser", text="no_such_quiz")
    context = _make_context(db_session)

    result = await enter_old_name(update, context)

    assert result == "ENTER_OLD_NAME"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "doesn't exist" in reply_text
    assert "no_such_quiz" in reply_text


# -- enter_new_name tests --

@pytest.mark.asyncio
async def test_enter_new_name_successful_rename(db_session):
    _insert_quiz(db_session, "testuser", "oldquiz")

    update = _make_update(username="testuser", text="newquiz")
    context = _make_context(db_session, user_data={"old_quiz_name": "oldquiz"})

    result = await enter_new_name(update, context)

    assert result == ConversationHandler.END
    reply_text = update.message.reply_text.call_args[0][0]
    assert "renamed" in reply_text.lower()
    assert "oldquiz" in reply_text
    assert "newquiz" in reply_text

    # Verify DB was updated
    session = db_session()
    old = session.query(QuizModel).filter_by(username="testuser", quizname="oldquiz").first()
    new = session.query(QuizModel).filter_by(username="testuser", quizname="newquiz").first()
    session.close()
    assert old is None
    assert new is not None


@pytest.mark.asyncio
async def test_enter_new_name_already_exists(db_session):
    _insert_quiz(db_session, "testuser", "oldquiz")
    _insert_quiz(db_session, "testuser", "newquiz")

    update = _make_update(username="testuser", text="newquiz")
    context = _make_context(db_session, user_data={"old_quiz_name": "oldquiz"})

    result = await enter_new_name(update, context)

    assert result == "ENTER_NEW_NAME"
    reply_text = update.message.reply_text.call_args[0][0]
    assert "already exists" in reply_text
    assert "newquiz" in reply_text


@pytest.mark.asyncio
async def test_enter_new_name_old_quiz_deleted_meanwhile(db_session):
    # Don't insert oldquiz — simulate it being deleted between steps
    update = _make_update(username="testuser", text="newquiz")
    context = _make_context(db_session, user_data={"old_quiz_name": "oldquiz"})

    result = await enter_new_name(update, context)

    assert result == ConversationHandler.END
    reply_text = update.message.reply_text.call_args[0][0]
    assert "doesn't exist anymore" in reply_text
