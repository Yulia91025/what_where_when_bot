import pytest
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from kts_backend.store.models.models import (
    Game,
    Player,
    GameScore,
    GameModel,
    PlayerModel,
    GameScoreModel,
)
from kts_backend.store.users.dataclasses import User
from kts_backend.store import Store
from tests.utils import check_empty_table_exists


class TestGamesStore:
    @pytest.mark.asyncio
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "games")
        await check_empty_table_exists(cli, "players")
        await check_empty_table_exists(cli, "gamescores")

    @pytest.mark.asyncio
    async def test_create_game(self, cli, store: Store):
        users = []
        user_1 = User(id=2222222, name="Meow", last_name="Meow Meow")
        user_2 = User(id=1111111, name="Name", last_name="Surname")
        users.append(user_1)
        users.append(user_2)
        chat_id = 1111
        game = await store.game.create_game(chat_id, users)

        assert type(game) is Game

        async with cli.app.database.session() as session:
            res = await session.execute(select(GameModel))
            games = res.scalars().all()

            res = await session.execute(select(PlayerModel))
            db_players = res.scalars().all()

            res = await session.execute(select(GameScoreModel))
            db_gamescores = res.scalars().all()

        assert len(games) == 1
        db_game = games[0]

        assert db_game.chat_id == chat_id

        assert type(db_game.created_at) == datetime

        assert len(db_players) == len(users)
        for db_player, user in zip(db_players, users):
            assert db_player.id == user.id
            assert db_player.name == user.name

        for gamescore in db_gamescores:
            assert gamescore.points == 0

    @pytest.mark.asyncio
    async def test_get_game(self, cli, store: Store, game_1: Game):
        game = await game_1
        assert game == await store.game.get_game(game.chat_id)

    @pytest.mark.asyncio
    async def test_check_cascade_delete(self, cli, game_1: Game):
        game = await game_1
        async with cli.app.database.session() as session:
            await session.execute(
                delete(GameModel).where(GameModel.id == game.id)
            )
            await session.commit()

            res = await session.execute(
                select(GameScoreModel).where(GameScoreModel.game_id == game.id)
            )
            db_scores = res.scalars().all()

            db_players = []
            for db_score in db_scores:
                res = await session.execute(
                    select(PlayerModel).where(
                        PlayerModel.id == db_score.player_id
                    )
                )
                db_players.append(res.scalar())

        assert len(db_scores) == 0
        assert len(db_players) == 0
