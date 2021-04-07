from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema

class RCQuestionOption(BaseTextModel):
    __tablename__ = 'rc_question_option'

    rc_question_id = Column(db.Integer, ForeignKey('rc_question.id'))
    rc_question = relationship("RCQuestion", back_populates="options")

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.rc_question_id = item.get('rc_question_id')

    def __repr__(self):
        return '<rc_question_option %r>' % self.id

class RCQuestionOptionSchema(BaseTextModelSchema):
    class Meta:
        model = RCQuestionOption

    rc_question_id = fields.Integer()


