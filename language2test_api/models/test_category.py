from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.test_type import TestType, TestTypeSchema
import datetime

class TestCategory(db.Model):
    __tablename__ = 'test_category'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    test_type_id = db.Column(db.Integer(), ForeignKey('test_type.id'))
    test_type = relationship("TestType")
    db.UniqueConstraint('name', 'test_type_id', name='_name_test_type_id')
    created_datetime = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, item):
        self.id = item.get('id')
        self.name = item.get('name')
        self.test_type_id = item.get('test_type_id')

    def __repr__(self):
        return '<test_category %s, %s>' % (self.user_id, str(self.created_datetime))

class TestCategorySchema(ma.ModelSchema):
    class Meta:
        model = TestCategory

    id = fields.Integer(dump_only=True)
    name = fields.String()
    test_type = fields.Nested(TestTypeSchema)
    test_type_id = fields.Integer()

