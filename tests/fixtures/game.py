import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from kts_backend.store.models.models import (
    Game,
    Player,
    GameScore,
    GameModel,
    PlayerModel,
    GameScoreModel,
)


@pytest.fixture
async def game_1_init(db_session: AsyncSession) -> Game:
    chat_id = 1111
    new_game = GameModel(chat_id=chat_id)
    async with db_session.begin() as session:
        session.add(new_game)

    return Game(
        id=new_game.id,
        created_at=new_game.created_at,
        chat_id=chat_id,
        players=[],
    )


@pytest.fixture
async def player_1_init(db_session: AsyncSession) -> Player:
    vk_id = 123456789
    name = "John"
    last_name = "Doe"

    async with db_session.begin() as session:
        new_player = PlayerModel(id=vk_id, name=name, last_name=last_name)

        session.add(new_player)

    return Player(vk_id=vk_id, name=name, last_name=last_name, score=None)


@pytest.fixture
async def player_2_init(db_session: AsyncSession) -> Player:
    vk_id = 111111111
    name = "Mary"
    last_name = "Jane"
    new_player = PlayerModel(id=vk_id, name=name, last_name=last_name)
    async with db_session.begin() as session:
        session.add(new_player)

    return Player(vk_id=vk_id, name=name, last_name=last_name, score=None)


@pytest.fixture
async def gamescore_1(db_session: AsyncSession) -> GameScore:
    points = 0
    async with db_session.begin() as session:
        gamescore = GameScoreModel(
            points=points, game_id=1, player_id=123456789
        )

        session.add(gamescore)

    return GameScore(points=points)


@pytest.fixture
async def gamescore_2(db_session: AsyncSession) -> GameScore:
    points = 3
    async with db_session.begin() as session:
        gamescore = GameScoreModel(
            points=points, game_id=1, player_id=111111111
        )

        session.add(gamescore)

    return GameScore(points=points)


@pytest.fixture
async def player_1(
    db_session: AsyncSession, player_1_init: Player, gamescore_1: GameScore
) -> Player:
    new_player = await player_1_init

    return Player(
        vk_id=new_player.vk_id,
        name=new_player.name,
        last_name=new_player.last_name,
        score=await gamescore_1,
    )


@pytest.fixture
async def player_2(
    db_session: AsyncSession, player_2_init: Player, gamescore_2: GameScore
) -> Player:
    new_player = await player_2_init

    return Player(
        vk_id=new_player.vk_id,
        name=new_player.name,
        last_name=new_player.last_name,
        score=await gamescore_2,
    )


@pytest.fixture
async def game_1(
    db_session: AsyncSession,
    game_1_init: Game,
    player_1: Player,
    player_2: Player,
) -> Game:
    new_game = await game_1_init

    players = []
    players.append(await player_1)
    players.append(await player_2)
    return Game(
        id=new_game.id,
        created_at=new_game.created_at,
        chat_id=new_game.chat_id,
        players=players,
    )


@pytest.fixture
async def game_2(db_session: AsyncSession) -> Game:
    chat_id = 1112
    new_game = GameModel(chat_id=chat_id)
    async with db_session.begin() as session:
        session.add(new_game)

    return Game(
        id=new_game.id,
        created_at=new_game.created_at,
        chat_id=chat_id,
        players=[]
    )
