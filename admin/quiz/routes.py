import typing

from admin.quiz.views import (
    QuestionAddView,
    QuestionListView,
)

if typing.TYPE_CHECKING:
    from admin.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/quiz.add_question", QuestionAddView)
    app.router.add_view("/quiz.list_questions", QuestionListView)
