import random
import json
import typing
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.store.vk_api.dataclasses import Message, Update, UpdateObject
from kts_backend.store.bot.poller import Poller
from kts_backend.store.bot.sendler import Sendler
from kts_backend.store.users.dataclasses import User

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.sendler: Optional[Sendler] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)

        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()
        self.sendler = Sendler(app.store)
        self.logger.info("start sending")
        await self.sendler.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.sendler:
            await self.sendler.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = int(data["ts"])
            self.logger.info(self.server)

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 30,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            raw_updates = data.get("updates", [])
            if len(raw_updates) != 0:
                self.ts = int(data["ts"])
                for update in raw_updates:
                    await self.app.store.updates_queue.put(
                        Update(
                            type=update["type"],
                            object=UpdateObject(
                                id=update["object"]["message"]["id"],
                                user_id=update["object"]["message"]["from_id"],
                                peer_id=update["object"]["message"]["peer_id"],
                                text=update["object"]["message"]["text"],
                                body=update["object"],
                            ),
                        )
                    )
            else:
                await self.app.store.updates_queue.put(
                    Update(
                        type= "Nothing",
                        object=UpdateObject(
                            id=None,
                            user_id=None,
                            peer_id=None,
                            text=None,
                            body=None,
                        ),
                    )
                )                

    async def send_message(self, message: Message) -> None:
        params = {
            "random_id": random.randint(1, 2**32),
            "peer_id": message.peer_id,
            "message": message.text,
            "access_token": self.app.config.bot.token,
        }  

        if message.keyboard is not None:
            params["keyboard"] = json.dumps(message.keyboard)

        if  message.user_id == message.peer_id:
            params["user_id"] = message.user_id

        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params=params,
            )
        ) as resp:
            data = await resp.json()
            info = dict()
            try:
                info["response"] = data["response"]
                info["peer_id"] = params["peer_id"]
                info["message"] = params["message"]
                self.logger.info(info)
            except KeyError:
                self.logger.info(data)

    async def _get_members(self, peer_id: int) -> list[User]:
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="messages.getConversationMembers",
                params={
                    "access_token": self.app.config.bot.token,
                    "peer_id": peer_id,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            profiles = data["response"]["profiles"]
            users = []
            for profile in profiles:
                users.append(
                    User(
                        id=int(profile["id"]),
                        name=profile["first_name"],
                        last_name=profile["last_name"],
                    )
                )
            return users
