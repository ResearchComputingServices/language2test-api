from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema
from language2test_api.models.cloze_question_option import ClozeQuestionOption, ClozeQuestionOptionSchema
from language2test_api.models.cloze_question_correctly_typed import ClozeQuestionCorrectlyTyped, ClozeQuestionCorrectlyTypedSchema
from language2test_api.models.cloze_question_incorrectly_typed import ClozeQuestionIncorrectlyTyped, ClozeQuestionIncorrectlyTypedSchema
from language2test_api.models.cloze_question_pending_typed import ClozeQuestionPendingTyped, ClozeQuestionPendingTypedSchema

class ClozeQuestion(BaseTextModel):
    __tablename__ = 'cloze_question'

    cloze_id = Column(db.Integer, ForeignKey('cloze.id'))
    options = relationship("ClozeQuestionOption", backref="cloze_question")
    difficulty = db.Column(db.Integer(), default=1)
    correct = db.Column(db.Integer)
    typed = db.Column(db.Boolean)

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.cloze_id = item.get('cloze_id')
        self.correct = item.get('correct')
        self.typed = item.get('typed')
        self.difficulty = item.get('difficulty')

    def __repr__(self):
        return '<cloze_question %r>' % self.id

class ClozeQuestionSchema(BaseTextModelSchema):
    class Meta:
        model = ClozeQuestion

    cloze_id = fields.Integer()
    options = fields.Nested(ClozeQuestionOptionSchema, many=True)
    correct = fields.Integer()
    typed = fields.Boolean()
    difficulty = fields.Integer()




