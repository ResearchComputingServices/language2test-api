from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema

class ClozeQuestionCorrectlyTyped(BaseTextModel):
    __tablename__ = 'cloze_question_correctly_typed'

    cloze_question_id = Column(db.Integer, ForeignKey('cloze_question.id'))

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.cloze_question_id = item.get('cloze_question_id')

    def __repr__(self):
        return '<cloze_question_correctly_typed %r>' % self.id

class ClozeQuestionCorrectlyTypedSchema(BaseTextModelSchema):
    class Meta:
        model = ClozeQuestionCorrectlyTyped

    cloze_question_id = fields.Integer()


