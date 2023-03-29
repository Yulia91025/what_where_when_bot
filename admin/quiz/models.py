from dataclasses import dataclass
from database.sqlalchemy_base import db

from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, Identity
from sqlalchemy.orm import relationship, backref


@dataclass
class Question:
    id: int
    title: str
    answers: list["Answer"]


@dataclass
class Answer:
    title: str


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(BigInteger, Identity(), primary_key=True)
    title = Column(String, unique=True)
    answers = relationship(
        "AnswerModel", back_populates="question", passive_deletes=True
    )


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(BigInteger, Identity(), primary_key=True)
    title = Column(String)
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question = relationship("QuestionModel")
