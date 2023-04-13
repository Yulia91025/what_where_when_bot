from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.store.models.models import (
    Game,
    Player,
    GameScore,
    GameModel,
    PlayerModel,
    GameScoreModel,
    GameQuestionModel,
)
from kts_backend.store.users.dataclasses import User
from admin.quiz.models import Question, QuestionModel

from sqlalchemy import select, insert, update


class GameAccessor(BaseAccessor):
    async def create_game(self, chat_id: int, users: list[User]) -> Game:
        stmt = insert(GameModel).values(chat_id=chat_id)

        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            stmt = select(GameModel).order_by(GameModel.id.desc())
            result = await session.execute(stmt)
            games = []
            for game_obj in result.scalars():
                games.append(
                    Game(game_obj.id, game_obj.created_at, chat_id, [])
                )
            new_game = games[0]

        players = []
        for user in users:
            players.append(
                await self.create_player(user.id, user.name, user.last_name)
            )
            gamescore = await self.create_game_score(new_game.id, user.id)
            players[len(players) - 1].gamescore = gamescore

        new_game.players = players
        questions = await self.app.store.quiz.get_11_random_questions()
        new_game.questions = questions
        for question in questions:
            await self.add_game_question(new_game.id, question.id)
        return new_game

    async def create_player(
        self, vk_id: int, name: str, last_name: str
    ) -> Player:
        stmt = insert(PlayerModel).values(
            id=vk_id, name=name, last_name=last_name
        )
        try:
            async with self.app.database.session() as session:
                result = await session.execute(stmt)
                await session.commit()

        except:
            pass
        return Player(vk_id=vk_id, name=name, last_name=last_name, score=None)

    async def create_game_score(
        self, game_id: int, player_id: int
    ) -> GameScore:
        stmt = insert(GameScoreModel).values(
            points=0, game_id=game_id, player_id=player_id
        )

        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            return GameScore(points=0)

    async def get_game(self, chat_id: int) -> Game:
        stmt = select(GameModel).where(GameModel.chat_id == chat_id)
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            game_obj = result.scalar()
            if game_obj is None:
                return None

            stmt = select(GameScoreModel).where(
                GameScoreModel.game_id == game_obj.id
            )
            result = await session.execute(stmt)
            gamescores = []
            players = []
            for gamescore_obj in result.scalars():
                gamescores.append(GameScore(points=gamescore_obj.points))
                stmt = select(PlayerModel).where(
                    PlayerModel.id == gamescore_obj.player_id
                )
                result = await session.execute(stmt)
                player_obj = result.scalar()
                players.append(
                    Player(
                        vk_id=player_obj.id,
                        name=player_obj.name,
                        last_name=player_obj.last_name,
                        score=GameScore(points=gamescore_obj.points),
                    )
                )

            stmt = select(GameQuestionModel).where(
                GameQuestionModel.game_id == game_obj.id
            )
            result = await session.execute(stmt)
            questions = []
            for gamequestion_obj in result.scalars():
                question = await self.app.store.quiz.get_question_by_id(
                    gamequestion_obj.question_id
                )
                questions.append(question)

            if len(questions) == 0:
                questions = None

            return Game(
                id=game_obj.id,
                created_at=game_obj.created_at,
                chat_id=chat_id,
                players=players,
                questions=questions,
            )

    async def get_players(self, chat_id: int) -> list[Player]:
        game = await self.get_game(chat_id)
        return game.players

    async def add_game_question(self, game_id: int, question_id: int):
        stmt = insert(GameQuestionModel).values(
            game_id=game_id, question_id=question_id
        )
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            await session.commit()

    async def get_game_questions(self, chat_id: int) -> list[Question]:
        game = await self.get_game(chat_id)
        return game.questions

    async def inc_game_points(self, game_id: int):
        stmt = (
            update(GameScoreModel)
            .values(points=GameScoreModel.points + 1)
            .where(GameScoreModel.game_id == game_id)
        )
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            await session.commit()

    async def get_current_game_points(self, game_id: int) -> int:
        stmt = select(GameScoreModel).where(GameScoreModel.game_id == game_id)
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            for scores_obj in result.scalars():
                points = scores_obj.points
                return points
