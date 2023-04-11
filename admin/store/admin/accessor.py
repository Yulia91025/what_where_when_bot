import typing
from hashlib import sha256
from typing import Optional

from sqlalchemy import select, insert

from admin.admin.models import Admin, AdminModel
from admin.base.base_accessor import BaseAccessor


if typing.TYPE_CHECKING:
    from admin.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        self.app = app
        admin = await self.create_admin(
            app.config.admin.email, app.config.admin.password
        )

    async def disconnect(self, _: "Application"):
        pass

    async def get_by_email(self, email: str) -> Admin | None:
        stmt = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
        admin_obj = result.scalar()
        if admin_obj is None:
            return None
        admin = Admin(admin_obj.id, admin_obj.email, admin_obj.password)
        return admin

    async def check_admin(self, email: str, password: str) -> Admin | None:
        admin = await self.get_by_email(email)
        psswrd = sha256(password.encode("utf-8")).hexdigest()
        if admin is None:
            return None
        if psswrd != admin.password: 
            return None
        return admin

    async def create_admin(self, email: str, password: str) -> Admin | None:
        psswrd = sha256(password.encode("utf-8")).hexdigest()
        stmt = insert(AdminModel).values(email=email, password=psswrd)
        try:
            async with self.app.database.session() as session:
                await session.execute(stmt)
                await session.commit()
            admin = await self.get_by_email(email)
            return admin
        except:
            return None
