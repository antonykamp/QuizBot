"""
Tests for SQLAlchemyPersistence.
"""
import pickle
import pytest

from quizbot.bot.models import ConversationState, UserData
from quizbot.bot.persistence import SQLAlchemyPersistence


# -- constructor --

def test_constructor_requires_url_or_factory():
    with pytest.raises(ValueError, match="Either database_url or session_factory"):
        SQLAlchemyPersistence()


def test_constructor_accepts_session_factory(db_session):
    p = SQLAlchemyPersistence(session_factory=db_session)
    assert p._Session is db_session


# -- get_conversations --

@pytest.mark.asyncio
async def test_get_conversations_empty(persistence):
    result = await persistence.get_conversations("create_quiz")
    assert result == {}


@pytest.mark.asyncio
async def test_get_conversations_returns_data(persistence, db_session):
    session = db_session()
    session.add(ConversationState(handler_name="create_quiz", chat_id=1, user_id=2, state="3"))
    session.commit()
    session.close()

    result = await persistence.get_conversations("create_quiz")
    assert result == {(1, 2): 3}


@pytest.mark.asyncio
async def test_get_conversations_filters_by_name(persistence, db_session):
    session = db_session()
    session.add(ConversationState(handler_name="create_quiz", chat_id=1, user_id=2, state="3"))
    session.add(ConversationState(handler_name="attempt_quiz", chat_id=1, user_id=2, state="5"))
    session.commit()
    session.close()

    result = await persistence.get_conversations("attempt_quiz")
    assert result == {(1, 2): 5}


# -- update_conversation --

@pytest.mark.asyncio
async def test_update_conversation_insert(persistence, db_session):
    await persistence.update_conversation("create_quiz", (10, 20), 3)

    session = db_session()
    row = session.query(ConversationState).first()
    assert row.handler_name == "create_quiz"
    assert row.chat_id == 10
    assert row.user_id == 20
    assert row.state == "3"
    session.close()


@pytest.mark.asyncio
async def test_update_conversation_update(persistence, db_session):
    await persistence.update_conversation("create_quiz", (10, 20), 3)
    await persistence.update_conversation("create_quiz", (10, 20), 7)

    session = db_session()
    rows = session.query(ConversationState).all()
    assert len(rows) == 1
    assert rows[0].state == "7"
    session.close()


@pytest.mark.asyncio
async def test_update_conversation_delete_on_end(persistence, db_session):
    await persistence.update_conversation("create_quiz", (10, 20), 3)
    await persistence.update_conversation("create_quiz", (10, 20), -1)

    session = db_session()
    assert session.query(ConversationState).count() == 0
    session.close()


@pytest.mark.asyncio
async def test_update_conversation_delete_on_none(persistence, db_session):
    await persistence.update_conversation("create_quiz", (10, 20), 3)
    await persistence.update_conversation("create_quiz", (10, 20), None)

    session = db_session()
    assert session.query(ConversationState).count() == 0
    session.close()


@pytest.mark.asyncio
async def test_update_conversation_delete_nonexistent_is_noop(persistence, db_session):
    await persistence.update_conversation("create_quiz", (10, 20), None)

    session = db_session()
    assert session.query(ConversationState).count() == 0
    session.close()


# -- get_user_data --

@pytest.mark.asyncio
async def test_get_user_data_empty(persistence):
    result = await persistence.get_user_data()
    assert result == {}


@pytest.mark.asyncio
async def test_get_user_data_returns_data(persistence, db_session):
    data = {"quiz": "in_progress", "score": 5}
    session = db_session()
    session.add(UserData(user_id=42, data=pickle.dumps(data)))
    session.commit()
    session.close()

    result = await persistence.get_user_data()
    assert result == {42: data}


@pytest.mark.asyncio
async def test_get_user_data_skips_corrupt(persistence, db_session):
    session = db_session()
    session.add(UserData(user_id=42, data=pickle.dumps({"ok": True})))
    session.add(UserData(user_id=99, data=b"not-valid-pickle"))
    session.commit()
    session.close()

    result = await persistence.get_user_data()
    assert result == {42: {"ok": True}}


# -- update_user_data --

@pytest.mark.asyncio
async def test_update_user_data_insert(persistence, db_session):
    await persistence.update_user_data(42, {"quiz": "in_progress"})

    session = db_session()
    row = session.query(UserData).first()
    assert row.user_id == 42
    assert pickle.loads(row.data) == {"quiz": "in_progress"}
    session.close()


@pytest.mark.asyncio
async def test_update_user_data_upsert(persistence, db_session):
    await persistence.update_user_data(42, {"step": 1})
    await persistence.update_user_data(42, {"step": 2})

    session = db_session()
    rows = session.query(UserData).all()
    assert len(rows) == 1
    assert pickle.loads(rows[0].data) == {"step": 2}
    session.close()


@pytest.mark.asyncio
async def test_update_user_data_deletes_empty(persistence, db_session):
    await persistence.update_user_data(42, {"step": 1})
    await persistence.update_user_data(42, {})

    session = db_session()
    assert session.query(UserData).count() == 0
    session.close()


# -- drop_user_data --

@pytest.mark.asyncio
async def test_drop_user_data(persistence, db_session):
    await persistence.update_user_data(42, {"step": 1})
    await persistence.drop_user_data(42)

    session = db_session()
    assert session.query(UserData).count() == 0
    session.close()


@pytest.mark.asyncio
async def test_drop_user_data_nonexistent_is_noop(persistence):
    await persistence.drop_user_data(999)


# -- no-op methods return correct defaults --

@pytest.mark.asyncio
async def test_get_bot_data_returns_empty_dict(persistence):
    assert await persistence.get_bot_data() == {}


@pytest.mark.asyncio
async def test_get_chat_data_returns_empty_dict(persistence):
    assert await persistence.get_chat_data() == {}


@pytest.mark.asyncio
async def test_get_callback_data_returns_none(persistence):
    assert await persistence.get_callback_data() is None


@pytest.mark.asyncio
async def test_noop_methods_do_not_raise(persistence):
    await persistence.update_bot_data({})
    await persistence.update_chat_data(1, {})
    await persistence.drop_chat_data(1)
    await persistence.update_callback_data(None)
    await persistence.refresh_user_data(1, {})
    await persistence.refresh_chat_data(1, {})
    await persistence.refresh_bot_data({})
    await persistence.flush()
