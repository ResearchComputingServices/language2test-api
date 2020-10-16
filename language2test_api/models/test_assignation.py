import datetime
from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_model import BaseModel, BaseModelSchema
from language2test_api.models.student_class import StudentClassSchema
from language2test_api.models.test import TestSchema

test_assignation_student_class = db.Table('test_assignation_student_class',
    db.Column('test_assignation_id', db.Integer, db.ForeignKey('test_assignation.id'), primary_key=True),
    db.Column('student_class_id', db.Integer, db.ForeignKey('student_class.id'), primary_key=True)
)

class TestAssignation(db.Model):
    __tablename__ = 'test_assignation'
    id = db.Column(db.Integer(), primary_key=True)
    test_id = db.Column(db.Integer, ForeignKey('test.id'))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    student_class = relationship("StudentClass", secondary=test_assignation_student_class)
    test = relationship("Test")


    def __init__(self, item):
        self.id = item.get('id')
        test = item.get('test')
        self.test_id = test['id']
        self.start_datetime = item.get('start_datetime')
        self.end_datetime = item.get('end_datetime')


    def __repr__(self):
        return '<test_assignation_to_class %r>' % self.name


class TestAssignationSchema(BaseModelSchema):
    class Meta:
        model = TestAssignation

    id = fields.Integer(dump_only=True)
    test_id = fields.Integer()
    start_datetime = fields.DateTime()
    end_datetime = fields.DateTime()
    student_class = fields.Nested(StudentClassSchema, many=True)
    test = fields.Nested(TestSchema)