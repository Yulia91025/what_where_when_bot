import typing

from admin.quiz.views import (
    QuestionAddView,
    QuestionListView,
    QuestionParseView,
    UnverifiedQuestionsListView,
    QuestionAcceptanceView,
    QuestionEditView,
    EditQuestionFormView,
    NewQuestionFormView,
    FindQuestionFormView,
    QuestionView,
    AcceptedQuestionsListView,
)

if typing.TYPE_CHECKING:
    from admin.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/quiz.new_question", NewQuestionFormView)
    app.router.add_view("/quiz.add_question", QuestionAddView)
    app.router.add_view("/quiz.list_questions", QuestionListView)
    app.router.add_view("/quiz.parse_questions", QuestionParseView)
    app.router.add_view(
        "/quiz.list_unverified_questions", UnverifiedQuestionsListView
    )
    app.router.add_view(
        "/quiz.list_accepted_questions", AcceptedQuestionsListView
    )
    app.router.add_view("/quiz.accept_question", QuestionAcceptanceView)
    app.router.add_view("/quiz.edit_question/{tail:.*}", EditQuestionFormView)
    app.router.add_view("/quiz.update_question", QuestionEditView)
    app.router.add_view("/quiz.find_question", FindQuestionFormView)
    app.router.add_view("/quiz.question/{tail:.*}", QuestionView)
