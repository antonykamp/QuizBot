from sqlalchemy import Column, Integer, String, LargeBinary, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class QuizModel(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, index=True)
    quizname = Column(String, nullable=False)
    quizinstance = Column(LargeBinary, nullable=False)

    __table_args__ = (
        UniqueConstraint('username', 'quizname'),
    )
