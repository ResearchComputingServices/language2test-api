from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.test_category import TestCategory, TestCategorySchema
from language2test_api.models.base_model import BaseModel, BaseModelSchema

class Writing(BaseModel):
    __tablename__ = 'writing'

    filename = db.Column(db.String())
    type = db.Column(db.String(), default='text')
    question = db.Column(db.String())
    word_limit = db.Column(db.Integer())
    time_limit = db.Column(db.Integer())
    test_category_id = db.Column(db.Integer(), ForeignKey('test_category.id'))
    test_category = relationship("TestCategory")

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.filename = item.get('filename') if item.get('filename') else ''
        self.type = item.get('type') if item.get('type') else 'text'
        self.question = item.get('question')
        self.word_limit = item.get('word_limit')
        self.time_limit = item.get('time_limit')
        self.test_category_id = item.get('test_category_id')

    def __repr__(self):
        return '<writing %r>' % self.name

class WritingSchema(BaseModelSchema):
    class Meta:
        model = Writing

    type = fields.String()
    filename = fields.String()
    question = fields.String()
    word_limit = fields.Integer()
    time_limit = fields.Integer()
    test_category = fields.Nested(TestCategorySchema)
    test_category_id = fields.Integer()
