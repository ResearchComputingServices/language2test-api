from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.test_category import TestCategory, TestCategorySchema
import datetime

class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    id = db.Column(db.Integer(), primary_key=True)
    word = db.Column(db.String(), unique=True, nullable=False)
    type = db.Column(db.String())
    difficulty = db.Column(db.Integer())
    correct = db.Column(db.Integer())
    time_limit= db.Column(db.Integer())
    options = relationship("VocabularyOption", back_populates="vocabulary")
    test_category_id = db.Column(db.Integer(), ForeignKey('test_category.id'))
    test_category = relationship("TestCategory")
    immutable = db.Column(db.Boolean, default=False)
    unremovable = db.Column(db.Boolean, default=False)
    created_datetime = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, item):
        self.id = item.get('id')
        self.word = item.get('word')
        self.type = item.get('type')
        self.difficulty = item.get('difficulty')
        self.correct = item.get('correct')
        self.time_limit = item.get('time_limit')
        self.test_category_id = item.get('test_category_id')
        self.immutable = item.get('immutable')
        self.unremovable = item.get('unremovable')

    def __repr__(self):
        return '<vocabulary %r>' % self.id

from language2test_api.models.vocabulary_option import VocabularyOption, VocabularyOptionSchema

class VocabularySchema(ma.ModelSchema):
    class Meta:
        model = Vocabulary

    id = fields.Integer(dump_only=True)
    word = fields.String()
    type = fields.String()
    difficulty = fields.String()
    correct = fields.Integer()
    time_limit = fields.Integer()
    options = fields.Nested(VocabularyOptionSchema, many=True)
    test_category = fields.Nested(TestCategorySchema)
    test_category_id = fields.Integer()
    immutable = fields.Boolean()
    unremovable = fields.Boolean()


