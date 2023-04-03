from datetime import datetime
from dataclasses import dataclass
from database.sqlalchemy_base import db

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    Identity,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from admin.quiz.models import Question, QuestionModel


@dataclass
class Game:
    id: int
    created_at: datetime
    chat_id: int
    players: list["Player"]
    questions: list[Question] = None


@dataclass
class Player:
    vk_id: int
    name: str
    last_name: str
    score: "GameScore"


@dataclass
class GameScore:
    points: int


class GameModel(db):
    __tablename__ = "games"
    id = Column(BigInteger, Identity(), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    chat_id = Column(BigInteger)


class PlayerModel(db):
    __tablename__ = "players"
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    last_name = Column(String)
    score = relationship(
        "GameScoreModel", back_populates="player", passive_deletes=True
    )


class GameScoreModel(db):
    __tablename__ = "gamescores"
    id = Column(BigInteger, Identity(), primary_key=True)
    points = Column(BigInteger)
    game_id = Column(
        BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    player_id = Column(
        BigInteger, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    game = relationship("GameModel")
    player = relationship("PlayerModel")


class GameQuestionModel(db):
    __tablename__ = "game_questions"
    id = Column(BigInteger, Identity(), primary_key=True)
    game_id = Column(
        BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    game = relationship("GameModel")
    question = relationship("QuestionModel")
