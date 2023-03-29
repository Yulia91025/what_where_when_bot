import typing
from asyncio import Queue as async_queue

from database.database import Database

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from kts_backend.store.users.accessor import UserAccessor
        from kts_backend.store.vk_api.accessor import VkApiAccessor
        from kts_backend.store.bot.manager import BotManager
        from kts_backend.store.game.accessor import GameAccessor
        from admin.store.quiz.accessor import QuizAccessor

        self.updates_queue = async_queue()
        self.messages_queue = async_queue()
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)
        self.user = UserAccessor(app)
        self.game = GameAccessor(app)
        self.quiz = QuizAccessor(app)


def setup_store(app: "Application", database: Database):
    app.database = database
    # app.on_startup.append(app.database.connect)
    # app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
