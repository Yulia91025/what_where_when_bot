from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.store.models.models import (
    Game,
    Player,
    GameScore,
    GameModel,
    PlayerModel,
    GameScoreModel,
)
from kts_backend.store.users.dataclasses import User

from sqlalchemy import select, insert


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
        return new_game

    async def create_player(
        self, vk_id: int, name: str, last_name: str
    ) -> Player:
        stmt = insert(PlayerModel).values(
            id=vk_id, name=name, last_name=last_name
        )

        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            return Player(
                vk_id=vk_id, name=name, last_name=last_name, score=None
            )

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

            return Game(
                id=game_obj.id,
                created_at=game_obj.created_at,
                chat_id=chat_id,
                players=players,
            )
