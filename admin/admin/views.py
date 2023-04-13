from aiohttp.web import HTTPForbidden, HTTPNotFound, HTTPConflict
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from admin.admin.schemes import AdminSchema
from admin.web.app import View
from admin.web.utils import json_response
from admin.web.mixins import AuthRequiredMixin

from aiohttp_jinja2 import template


class AdminAddView(View):
    @docs(tags=["admin"], summary="Add new administrator")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        try:
            data = self.request["data"]
        except KeyError:
            data = await self.request.text()
        admin = await self.request.app.store.admins.create_admin(
            data["email"], data["password"]
        )
        if admin is None:
            raise HTTPConflict
        session = await new_session(request=self.request)
        session["admin"] = {}
        session["admin"]["email"] = admin.email
        session["admin"]["password"] = admin.password
        session["admin"]["id"] = admin.id
        return json_response(data=AdminSchema().dump(admin))


class AdminAuthView(View):
    @docs(tags=["admin"], summary="Administrator authentication")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        try:
            data = self.request["data"]
        except KeyError:
            data = await self.request.text()
        admin = await self.request.app.store.admins.check_admin(
            data["email"], data["password"]
        )
        if admin is None:
            raise HTTPForbidden
        session = await new_session(request=self.request)
        session["admin"] = {}
        session["admin"]["email"] = admin.email
        session["admin"]["password"] = admin.password
        session["admin"]["id"] = admin.id
        return json_response(data=AdminSchema().dump(admin))


@template("admin_login.html")
class AdminLoginView(View):
    @docs(tags=["admin"], summary="Administrator login")
    async def get(self):
        return {"title": "Войти или зарегистрироваться"}


@template("admin.html")
class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["admin"], summary="Current Administrator")
    async def get(self):
        admin_info = self.request.admin
        email = admin_info.email
        admin = await self.request.app.store.admins.get_by_email(email)
        if admin is None:
            return {"title": "Вы не авторизировались!"}
        return {
            "title": "Страница администратора",
            "email": admin.email,
            "id": admin.id,
        }
