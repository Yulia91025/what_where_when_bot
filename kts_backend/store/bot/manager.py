import typing
from logging import getLogger

from kts_backend.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self._statements = ["start", "vote", "results"]
        self.app = app
        self.bot = None
        self.state_indx = 0
        self.state = self._statements[self.state_indx]
        self.logger = getLogger("handler")

    async def handle_updates(self, update: Update):
        if update.type == "message_new":
            await self.app.store.messages_queue.put(
                Message(
                    user_id=update.object.user_id,
                    text="Привет!",
                    peer_id=update.object.peer_id,
                )
            )
