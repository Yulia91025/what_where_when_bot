import typing

from admin.admin.views import AdminCurrentView, AdminAddView

if typing.TYPE_CHECKING:
    from admin.web.app import Application


def setup_routes(app: "Application"):
    from admin.admin.views import AdminLoginView

    app.router.add_view("/admin.add", AdminAddView)
    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)
