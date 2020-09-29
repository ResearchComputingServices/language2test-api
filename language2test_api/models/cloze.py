from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_model import BaseModel, BaseModelSchema
from language2test_api.models.test_category import TestCategory, TestCategorySchema
from language2test_api.models.cloze_question import ClozeQuestion, ClozeQuestionSchema

class Cloze(BaseModel):
    __tablename__ = 'cloze'

    text = db.Column(db.String())
    filename = db.Column(db.String())
    type = db.Column(db.String(), default='text')
    time_limit = db.Column(db.Integer())
    questions = relationship("ClozeQuestion", backref="cloze")
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
        return '<cloze %r>' % self.id

class ClozeSchema(BaseModelSchema):
    class Meta:
        model = Cloze

    text = fields.String()
    type = fields.String()
    filename = fields.String()
    time_limit = fields.Integer()
    questions = fields.Nested(ClozeQuestionSchema, many=True)
    test_category = fields.Nested(TestCategorySchema)
    test_category_id = fields.Integer()

