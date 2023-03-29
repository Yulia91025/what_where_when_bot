from aiohttp.web import HTTPForbidden, HTTPNotFound, HTTPConflict
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from admin.admin.schemes import AdminSchema
from admin.web.app import View
from admin.web.utils import json_response
from admin.web.mixins import AuthRequiredMixin


class AdminAddView(View):
    @docs(tags=["admin"], summary="Add new administrator")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = self.request["data"]
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


class AdminLoginView(View):
    @docs(tags=["admin"], summary="Administrator authorization")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = self.request["data"]
        admin = await self.request.app.store.admins.get_by_email(data["email"])
        if admin is None:
            raise HTTPForbidden
        session = await new_session(request=self.request)
        session["admin"] = {}
        session["admin"]["email"] = admin.email
        session["admin"]["password"] = admin.password
        session["admin"]["id"] = admin.id
        return json_response(data=AdminSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["admin"], summary="Current Administrator")
    @response_schema(AdminSchema, 200)
    async def get(self):
        admin_info = self.request.admin
        email = admin_info.email
        admin = await self.request.app.store.admins.get_by_email(email)
        if admin is None:
            raise HTTPNotFound
        return json_response(data=AdminSchema().dump(admin))
