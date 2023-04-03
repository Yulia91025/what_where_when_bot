import typing

from database.database import Database

if typing.TYPE_CHECKING:
    from admin.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from admin.store.admin.accessor import AdminAccessor
        from admin.store.quiz.accessor import QuizAccessor

        self.quizzes = QuizAccessor(app)
        self.admins = AdminAccessor(app)

        app.on_cleanup.append(self.admins.disconnect)


def setup_store(app: "Application", database: Database):
    app.database = database
    # app.on_startup.append(app.database.connect)
    # app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
