import typing

from admin.quiz.views import (
    QuestionAddView,
    QuestionListView,
    QuestionParseView,
    UnverifiedQuestionsListView,
    QuestionAcceptanceView,
    QuestionEditView
)

if typing.TYPE_CHECKING:
    from admin.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/quiz.add_question", QuestionAddView)
    app.router.add_view("/quiz.list_questions", QuestionListView)
    app.router.add_view("/quiz.parse_questions", QuestionParseView)
    app.router.add_view("/quiz.list_unverified_questions", UnverifiedQuestionsListView)
    app.router.add_view("/quiz.accept_question", QuestionAcceptanceView)
    app.router.add_view("/quiz.edit_question", QuestionEditView)
