import asyncio
from asyncio import Task
from typing import Optional

from kts_backend.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        await self.store.updates_queue.put(0)
        await self.poll_task

    async def poll(self):
        while self.is_running:
            updt_for_timer = False
            chat_id = None
            for chat in self.store.bots_manager.timer_flags:
                if self.store.bots_manager.timer_flags[chat]:
                    updt_for_timer = True
                    chat_id = chat
                    break
            if updt_for_timer:
                self.store.bots_manager.timer_flags[chat_id] = False
                update = await self.store.updates_queue.get()
                if update != 0:
                    await self.store.bots_manager.handle_updates(update)
            else:
                if self.store.updates_queue.empty():
                    await self.store.vk_api.poll()
                update = await self.store.updates_queue.get()
                if update != 0:
                    await self.store.bots_manager.handle_updates(update)
