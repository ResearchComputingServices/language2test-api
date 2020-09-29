from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.user import User, UserSchema
from language2test_api.models.base_model import BaseModel, BaseModelSchema

student_student_class = db.Table('student_student_class',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('student_class_id', db.Integer, db.ForeignKey('student_class.id'), primary_key=True)
)

class StudentClass(BaseModel):
    __tablename__ = 'student_class'

    display = db.Column(db.String())
    instructor_id = db.Column(db.Integer(), ForeignKey('user.id'))
    instructor = relationship("User")
    student_student_class = relationship("User", secondary=student_student_class)

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.display = item.get('display')
        self.instructor_id = item.get('instructor_id')

    def __repr__(self):
        return '<student_class %r>' % self.name

class StudentClassSchema(BaseModelSchema):
    class Meta:
        model = StudentClass

    display = fields.String()
    instructor_id = fields.String()
    instructor = fields.Nested(UserSchema)
    student_student_class = fields.Nested(UserSchema, many=True)
