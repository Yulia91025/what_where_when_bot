from aiohttp_apispec import querystring_schema, request_schema, response_schema
from admin.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    QuestionAcceptanceSchema,
    QuestionEditSchema,
    QuestionFindSchema,
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

from aiohttp_jinja2 import template


@template("new_question.html")
class NewQuestionFormView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="New question")
    async def get(self):
        return {"title": "Введите вопрос"}


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Add question")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        try:
            data = self.request["data"]
            title = data["title"]
            answers = data["answers"]
        except KeyError:
            try:
                text = await self.request.text
                title = text["title"]
                answers = text["answers"]
            except:
                raise HTTPBadRequest
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


@template("questions.html")
class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="List of questions")
    @response_schema(ListQuestionSchema, 200)
    async def get(self):
        questions = await self.request.app.store.quizzes.list_questions()
        raw_questions = [
            QuestionSchema().dump(question) for question in questions
        ]
        return {"title": "Список вопросов", "questions": raw_questions}


@template("questions.html")
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
        return {"title": "Скачанные сейчас вопросы", "questions": raw_questions}


@template("questions.html")
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
        return {"title": "Непроверенные вопросы", "questions": raw_questions}


@template("questions.html")
class AcceptedQuestionsListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="List accepted questions")
    async def get(self):
        questions = (
            await self.request.app.store.quizzes.list_accepted_questions()
        )
        raw_questions = [
            QuestionSchema().dump(question) for question in questions
        ]
        return {"title": "Принятые вопросы", "questions": raw_questions}


class QuestionAcceptanceView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Question acceptance")
    @request_schema(QuestionAcceptanceSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        try:
            data = self.request["data"]
            id = data["id"]
            accepted = data["accepted"]
        except KeyError:
            try:
                text = await self.request.text
                id = text["id"]
                accepted = text["accepted"]
            except:
                raise HTTPBadRequest

        await self.request.app.store.quizzes.question_acceptance(id, accepted)
        question = await self.request.app.store.quizzes.get_question_by_id(id)
        return json_response(data=QuestionSchema().dump(question))


class QuestionEditView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Edit answers")
    @request_schema(QuestionEditSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        try:
            data = self.request["data"]
        except KeyError:
            data = await self.request.text
        id = data["id"]
        try:
            title = data["title"]
            if not title:
                title = None
        except KeyError:
            title = None
        try:
            answers_str = data["answers"]
            answers = []
            for ans in answers_str:
                answers.append(Answer(title=ans["title"]))
            if len(answers) == 0:
                answers = None
        except KeyError:
            answers = None

        await self.request.app.store.quizzes.edit_question(id, title, answers)
        question = await self.request.app.store.quizzes.get_question_by_id(id)
        return json_response(data=QuestionSchema().dump(question))


@template("edit_question.html")
class EditQuestionFormView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Form to edit question")
    async def get(self):
        id = self.request.rel_url.query.get("id")
        if not id:
            id = None
        question = await self.request.app.store.quizzes.get_question_by_id(
            int(id)
        )
        return {"title": "Редактор вопроса", "question": question, "id": id}


@template("question.html")
class QuestionView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Find question")
    async def get(self):
        try:
            id = self.request.rel_url.query.get("id")
            if not id:
                id = None
        except:
            id = None
        try:
            title = self.request.rel_url.query.get("title")
            if not title:
                title = None
        except:
            title = None
        if id is not None:
            question = await self.request.app.store.quizzes.get_question_by_id(
                int(id)
            )
        elif title is not None:
            question = (
                await self.request.app.store.quizzes.get_question_by_title(
                    title
                )
            )
        else:
            raise HTTPBadRequest
        if question is None:
            return {
                "title": "Вопрос не найден!",
                "question": question,
                "id": id,
            }
        return {"title": "Вопрос", "question": question, "id": id}


@template("find_question.html")
class FindQuestionFormView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Form to find question")
    async def get(self):
        return {"title": "Поиск вопроса"}
