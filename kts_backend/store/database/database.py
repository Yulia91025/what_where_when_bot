from typing import Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from kts_backend.store.database.sqlalchemy_base import db

if TYPE_CHECKING:
    from kts_backend.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(
            "postgresql+asyncpg://kts_user:kts_pass@0.0.0.0/botdb", echo=True
        )
        async with self._engine.begin() as conn:
            await conn.run_sync(db.metadata.drop_all)
            await conn.run_sync(db.metadata.create_all)
        self.session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def disconnect(self, *_: list, **__: dict) -> None:
        # await self.session.close()
        # await self._engine.dispose()
        pass
