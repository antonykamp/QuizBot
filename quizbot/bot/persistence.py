"""
SQLAlchemy-backed persistence for python-telegram-bot.

Persists conversation states and user_data to PostgreSQL so that
in-progress quiz creation / attempt state survives service restarts.
"""

import asyncio
import logging
import pickle

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from telegram.ext import BasePersistence, PersistenceInput

from quizbot.bot.models import ConversationState, UserData

logger = logging.getLogger(__name__)


class SQLAlchemyPersistence(BasePersistence):
    """Stores conversation states and user_data in a SQL database."""

    def __init__(self, database_url=None, session_factory=None, update_interval=5):
        if database_url is None and session_factory is None:
            raise ValueError("Either database_url or session_factory must be provided")

        super().__init__(
            store_data=PersistenceInput(
                bot_data=False, chat_data=False, callback_data=False, user_data=True
            ),
            update_interval=update_interval,
        )

        if session_factory is not None:
            self._Session = session_factory
        else:
            engine = create_engine(database_url)
            self._Session = sessionmaker(bind=engine)

    # -- conversations --

    async def get_conversations(self, name):
        def _load():
            session = self._Session()
            try:
                rows = session.query(ConversationState).filter_by(handler_name=name).all()
                def _parse_state(s):
                    try:
                        return int(s)
                    except ValueError:
                        return s

                return {(row.chat_id, row.user_id): _parse_state(row.state) for row in rows}
            finally:
                session.close()

        return await asyncio.to_thread(_load)

    async def update_conversation(self, name, key, new_state):
        def _update():
            session = self._Session()
            try:
                chat_id, user_id = key
                row = (
                    session.query(ConversationState)
                    .filter_by(handler_name=name, chat_id=chat_id, user_id=user_id)
                    .first()
                )

                if new_state is None or new_state == -1:
                    if row:
                        session.delete(row)
                        session.commit()
                    return

                if row:
                    row.state = str(new_state)
                else:
                    session.add(ConversationState(
                        handler_name=name,
                        chat_id=chat_id,
                        user_id=user_id,
                        state=str(new_state),
                    ))
                session.commit()
            finally:
                session.close()

        await asyncio.to_thread(_update)

    # -- user_data --

    async def get_user_data(self):
        def _load():
            session = self._Session()
            try:
                result = {}
                for row in session.query(UserData).all():
                    try:
                        result[row.user_id] = pickle.loads(row.data)
                    except Exception:
                        logger.warning("Corrupt user_data for user_id=%s, skipping", row.user_id)
                return result
            finally:
                session.close()

        return await asyncio.to_thread(_load)

    async def update_user_data(self, user_id, data):
        def _update():
            session = self._Session()
            try:
                row = session.query(UserData).filter_by(user_id=user_id).first()
                if not data:
                    if row:
                        session.delete(row)
                        session.commit()
                    return

                blob = pickle.dumps(data)
                if row:
                    row.data = blob
                else:
                    session.add(UserData(user_id=user_id, data=blob))
                session.commit()
            finally:
                session.close()

        await asyncio.to_thread(_update)

    async def drop_user_data(self, user_id):
        def _drop():
            session = self._Session()
            try:
                row = session.query(UserData).filter_by(user_id=user_id).first()
                if row:
                    session.delete(row)
                    session.commit()
            finally:
                session.close()

        await asyncio.to_thread(_drop)

    # -- refresh (no-op: we don't need to refresh from DB before each callback) --

    async def refresh_user_data(self, user_id, user_data):
        pass

    async def refresh_chat_data(self, chat_id, chat_data):
        pass

    async def refresh_bot_data(self, bot_data):
        pass

    # -- bot_data / chat_data / callback_data: not persisted --

    async def get_bot_data(self):
        return {}

    async def update_bot_data(self, data):
        pass

    async def get_chat_data(self):
        return {}

    async def update_chat_data(self, chat_id, data):
        pass

    async def drop_chat_data(self, chat_id):
        pass

    async def get_callback_data(self):
        return None

    async def update_callback_data(self, data):
        pass

    # -- flush --

    async def flush(self):
        pass
