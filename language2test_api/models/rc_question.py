from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema

class RCQuestion(BaseTextModel):
    __tablename__ = 'rc_question'

    rc_id = Column(db.Integer, ForeignKey('rc.id'))
    rc = relationship("RC", back_populates="questions")
    options = relationship("RCQuestionOption", back_populates="rc_question")
    difficulty = db.Column(db.Integer(), default=1)
    correct = db.Column(db.Integer)

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.rc_id = item.get('rc_id')
        self.correct = item.get('correct')
        self.difficulty = item.get('difficulty')

    def __repr__(self):
        return '<rc_question %r>' % self.id

from language2test_api.models.rc_question_option import RCQuestionOption, RCQuestionOptionSchema

class RCQuestionSchema(BaseTextModelSchema):
    class Meta:
        model = RCQuestion

    rc_id = fields.Integer()
    options = fields.Nested(RCQuestionOptionSchema, many=True)
    correct = fields.Integer()
    difficulty = fields.Integer()

