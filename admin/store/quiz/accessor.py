import random
from typing import Optional

from admin.base.base_accessor import BaseAccessor
from admin.quiz.models import Answer, Question, AnswerModel, QuestionModel

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from aiohttp.web_exceptions import HTTPBadRequest


class QuizAccessor(BaseAccessor):
    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:
        for answer in answers:
            stmt = insert(AnswerModel).values(
                title=str(answer.title), question_id=question_id
            )
            try:
                async with self.app.database.session() as session:
                    await session.execute(stmt)
                    await session.commit()
            except:
                return None
        return answers

    async def create_question(
        self, title: str, answers: list[Answer]
    ) -> Question:
        if len(answers) == 0:
            raise HTTPBadRequest
        for ans in answers:
            if ans.title is None:
                raise HTTPBadRequest
        try:
            stmt = insert(QuestionModel).values(
                title=title,
            )
        except Exception as e:
            raise IntegrityError("'title' is required field", title, e.orig)
        try:
            async with self.app.database.session() as session:
                await session.execute(stmt)
                await session.commit()
            question = await self.get_question_by_title(title)
            question.answers = answers
            answers_objs = await self.create_answers(question.id, answers)
            return question
        except Exception as e:
            raise IntegrityError("'title' must be unique", title, e.orig)

    async def get_question_by_title(self, title: str) -> Question | None:
        stmt = select(QuestionModel).where(QuestionModel.title == title)
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            question_obj = result.scalar()
            if question_obj is None:
                return None
            stmt = select(AnswerModel).where(
                AnswerModel.question_id == question_obj.id
            )
            result = await session.execute(stmt)
            answers = []
            for answer_obj in result.scalars():
                answers.append(Answer(answer_obj.title))
            question = Question(question_obj.id, question_obj.title, answers)
            return question

    async def get_question_by_id(self, id: int) -> Question | None:
        stmt = select(QuestionModel).where(QuestionModel.id == id)
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            question_obj = result.scalar()
            if question_obj is None:
                return None
            stmt = select(AnswerModel).where(
                AnswerModel.question_id == question_obj.id
            )
            result = await session.execute(stmt)
            answers = []
            for answer_obj in result.scalars():
                answers.append(Answer(answer_obj.title))
            question = Question(question_obj.id, question_obj.title, answers)
            return question

    async def list_questions(self) -> list[Question]:
        questions = []
        stmt = select(QuestionModel)
        async with self.app.database.session() as session:
            result = await session.execute(stmt)
            for question_obj in result.scalars():
                question = await self.get_question_by_title(question_obj.title)
                questions.append(question)
            return questions

    async def get_11_random_questions(self) -> list[Question]:
        all_questions = await self.list_questions()
        num_questions = len(all_questions)
        if num_questions < 11:
            return None
        indxs = random.sample(range(1, num_questions), 11)
        questions = []
        for i in indxs:
            questions.append(all_questions[i])
        return questions
