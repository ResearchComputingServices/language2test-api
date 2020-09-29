from pprint import pformat

from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_model import BaseModel, BaseModelSchema
from language2test_api.models.test_category import TestCategory, TestCategorySchema

class RC(BaseModel):
    __tablename__ = 'rc'

    text = db.Column(db.String())
    filename = db.Column(db.String())
    type = db.Column(db.String(), default='text')
    time_limit = db.Column(db.Integer())
    questions = relationship("RCQuestion", back_populates="rc")
    test_category_id = db.Column(db.Integer(), ForeignKey('test_category.id'))
    test_category = relationship("TestCategory")

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.text = item.get('text')
        self.type = item.get('type') if item.get('type') else 'text'
        self.time_limit = item.get('time_limit')
        self.filename = item.get('filename') if item.get('filename') else ''
        self.test_category_id = item.get('test_category_id')

    def __repr__(self):
        return '<rc %r>' % self.id

from language2test_api.models.rc_question import RCQuestion, RCQuestionSchema

class RCSchema(BaseModelSchema):
    class Meta:
        model = RC

    text = fields.String()
    type = fields.String()
    filename = fields.String()
    time_limit = fields.Integer()
    questions = fields.Nested(RCQuestionSchema, many=True)
    test_category = fields.Nested(TestCategorySchema)
    test_category_id = fields.Integer()

