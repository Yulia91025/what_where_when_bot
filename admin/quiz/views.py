from aiohttp_apispec import querystring_schema, request_schema, response_schema
from admin.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
)
from admin.quiz.models import Answer
from admin.web.schemes import OkResponseSchema
from admin.web.app import View
from admin.web.utils import json_response
from admin.web.mixins import AuthRequiredMixin

from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
    querystring_schema,
)
from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="New question")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = self.request["data"]
        if not data:
            raise HTTPBadRequest
        title = data["title"]
        answers = data["answers"]
        question = await self.request.app.store.quizzes.get_question_by_title(
            title
        )
        if question:
            raise HTTPConflict
        if type(answers[0]) is dict:
            answers_class = [Answer(title=ans["title"]) for ans in answers]
        else:
            answers_class = answers
        question = await self.store.quizzes.create_question(
            title, answers_class
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="List of questions")
    @response_schema(ListQuestionSchema, 200)
    async def get(self):
        questions = await self.request.app.store.quizzes.list_questions()
        raw_questions = [
            QuestionSchema().dump(question) for question in questions
        ]
        return json_response(data={"questions": raw_questions})
