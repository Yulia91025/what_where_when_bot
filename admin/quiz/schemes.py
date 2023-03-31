from marshmallow import Schema, fields


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    answers = fields.Nested("AnswerSchema", many=True, required=True)
    accepted = fields.Boolean(required=False)


class AnswerSchema(Schema):
    title = fields.Str(required=True)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)


class QuestionAcceptanceSchema(Schema):
    id = fields.Int(required=True)
    accepted = fields.Boolean(required=True)


class QuestionEditSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=False)
    answers = fields.Nested("AnswerSchema", many=True, required=False)
