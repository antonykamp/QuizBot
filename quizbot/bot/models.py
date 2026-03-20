from sqlalchemy import Column, Integer, String, LargeBinary, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class QuizModel(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, index=True)
    quizname = Column(String, nullable=False)
    quizinstance = Column(LargeBinary, nullable=False)
    password = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint('username', 'quizname'),
    )


class ConversationState(Base):
    __tablename__ = 'conversation_states'

    id = Column(Integer, primary_key=True)
    handler_name = Column(String, nullable=False, index=True)
    chat_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    state = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('handler_name', 'chat_id', 'user_id'),
    )


class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    data = Column(LargeBinary, nullable=False)
