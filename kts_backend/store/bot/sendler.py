import asyncio
from asyncio import Task
from typing import Optional

from kts_backend.store import Store

from kts_backend.store.vk_api.dataclasses import Message, Update, UpdateObject


class Sendler:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.send_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.send_task = asyncio.create_task(self.send())

    async def stop(self):
        self.is_running = False
        await self.store.messages_queue.put(0)
        await self.send_task

    async def send(self):
        while self.is_running:
            message = await self.store.messages_queue.get()
            if message != 0:
                await self.store.vk_api.send_message(message)
