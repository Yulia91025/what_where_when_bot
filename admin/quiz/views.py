from aiohttp_apispec import querystring_schema, request_schema, response_schema
from admin.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    QuestionAcceptanceSchema,
    QuestionEditSchema,
)
from admin.quiz.models import Answer
from admin.web.schemes import OkResponseSchema
from admin.web.app import View
from admin.web.utils import json_response
from admin.web.mixins import AuthRequiredMixin
from admin.quiz.questions_parser import QuestionParser

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
            title, answers_class, True
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


class QuestionParseView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Parse questions")
    @response_schema(ListQuestionSchema, 200)
    async def get(self):
        parser = QuestionParser()
        questions_str, answers_str = await parser.parse_main()
        questions = []
        for i in range(len(questions_str)):
            answer = Answer(answers_str[i])
            try:
                question = await self.request.app.store.quizzes.create_question(
                    questions_str[i], [answer]
                )
                questions.append(question)
            except:
                pass
        raw_questions = [
            QuestionSchema().dump(question) for question in questions
        ]
        return json_response(data={"questions": raw_questions})


class UnverifiedQuestionsListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="List unverified questions")
    @response_schema(ListQuestionSchema, 200)
    async def get(self):
        questions = (
            await self.request.app.store.quizzes.list_unverified_questions()
        )
        raw_questions = [
            QuestionSchema().dump(question) for question in questions
        ]
        return json_response(data={"questions": raw_questions})


class QuestionAcceptanceView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Question acceptance")
    @request_schema(QuestionAcceptanceSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = self.request["data"]
        if not data:
            raise HTTPBadRequest
        question_id = data["id"]
        question_accepted = data["accepted"]
        await self.request.app.store.quizzes.question_acceptance(
            question_id, question_accepted
        )
        question = await self.request.app.store.quizzes.get_question_by_id(
            question_id
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionEditView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Edit answers")
    @request_schema(QuestionEditSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = self.request["data"]
        if not data:
            raise HTTPBadRequest
        question_id = data["id"]
        try:
            question_title = data["title"]
        except KeyError:
            question_title = None
        try:
            answers_str = data["answers"]
            answers = []
            for ans in answers_str:
                answers.append(Answer(title=ans["title"]))
        except KeyError:
            answers = None

        await self.request.app.store.quizzes.edit_question(
            question_id, question_title, answers
        )
        question = await self.request.app.store.quizzes.get_question_by_id(
            question_id
        )
        return json_response(data=QuestionSchema().dump(question))
