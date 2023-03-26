import typing

from kts_backend.base.base_accessor import BaseAccessor


if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class UserAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        self.app = app

    async def disconnect(self, _: "Application"):
        pass
