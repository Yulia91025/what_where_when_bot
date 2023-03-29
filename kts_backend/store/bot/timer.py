import time
import asyncio
from asyncio import Task
from typing import Optional

from kts_backend.store.bot.manager import GameState


class Timer:
    def __init__(self, gamestate: GameState):
        self.gamestate = gamestate
        self.is_running = False
        self.time = None
        self.task: Optional[Task] = None

    async def start(self, update):
        self.is_running = True
        self.time = time.time()
        self.task = asyncio.create_task(self.t(update))

    async def stop(self):
        self.is_running = False
        await self.task.cancel()

    async def t(self, update):
        while self.is_running and time.time() - self.time < 60.0:
            if self.gamestate.current_state == self.gamestate.choose_resp:
                self.is_running = False
            else:
                await self.gamestate.bot.app.store.vk_api.poll()
                await self.gamestate.bot.app.store.updates_queue.get()
        if self.gamestate.current_state == self.gamestate.timer:
            self.gamestate.current_state = self.gamestate.choose_resp
            await self.gamestate.new_message(
                update,
                f"Время вышло! [id{self.gamestate.captain_id}|Капитан], укажите на отвечающего (через @)",
            )
