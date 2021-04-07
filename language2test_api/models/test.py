from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.vocabulary import Vocabulary, VocabularySchema
from language2test_api.models.rc import RC, RCSchema
from language2test_api.models.cloze import Cloze, ClozeSchema
from language2test_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from language2test_api.models.student_class import StudentClass, StudentClassSchema
from language2test_api.models.writing import Writing, WritingSchema
from language2test_api.models.base_model import BaseModel, BaseModelSchema
from sqlalchemy import func, ForeignKey, Sequence


from language2test_api.models.mutable_list import MutableList
from sqlalchemy.dialects.postgresql import ARRAY

test_vocabulary = db.Table('test_vocabulary',
    db.Column('vocabulary_id', db.Integer, db.ForeignKey('vocabulary.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True)
)

test_rc = db.Table('test_rc',
    db.Column('rc_id', db.Integer, db.ForeignKey('rc.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True)
)

test_cloze = db.Table('test_cloze',
    db.Column('cloze_id', db.Integer, db.ForeignKey('cloze.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True)
)

test_writing = db.Table('test_writing',
    db.Column('writing_id', db.Integer, db.ForeignKey('writing.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True)
)

test_user_field_category = db.Table('test_user_field_category',
    db.Column('user_field_category_id', db.Integer, db.ForeignKey('user_field_category.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True)
)

mandatory_test_user_field_category = db.Table('mandatory_test_user_field_category',
    db.Column('user_field_category_id', db.Integer, db.ForeignKey('user_field_category.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True)
)

class Test(BaseModel):
    __tablename__ = 'test'

    order = db.Column(
        MutableList.as_mutable(ARRAY(db.String())),
        server_default="{}"
    )
    test_vocabulary = relationship("Vocabulary", secondary=test_vocabulary)
    test_rc = relationship("RC", secondary=test_rc)
    test_cloze = relationship("Cloze", secondary=test_cloze)
    test_writing = relationship("Writing", secondary=test_writing)
    test_user_field_category = relationship("UserFieldCategory", secondary=test_user_field_category)
    mandatory_test_user_field_category = relationship("UserFieldCategory", secondary=mandatory_test_user_field_category)
    immutable = db.Column(db.Boolean, default=False)
    unremovable = db.Column(db.Boolean, default=False)
    cloned_from_id = db.Column(db.Integer(), ForeignKey('test.id'))
    created_by_user_id = db.Column(db.Integer(), ForeignKey('user.id'))
    created_by_user = relationship("User")

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.created_by_user_id = item.get('created_by_user_id')
        self.cloned_from_id = item.get('cloned_from_id')

    def __repr__(self):
        return '<test %r>' % self.id

from language2test_api.models.user import UserSchema

class TestSchema(BaseModelSchema):
    class Meta:
        model = Test

    order = fields.List(fields.String())
    test_vocabulary = fields.Nested(VocabularySchema, many=True)
    test_rc = fields.Nested(RCSchema, many=True)
    test_cloze = fields.Nested(ClozeSchema, many=True)
    test_writing = fields.Nested(WritingSchema, many=True)
    test_user_field_category = fields.Nested(UserFieldCategorySchema, many=True)
    mandatory_test_user_field_category = fields.Nested(UserFieldCategorySchema, many=True)
    immutable = fields.Boolean()
    unremovable = fields.Boolean()
    cloned_from_id = fields.Integer()
    created_by_user_id = fields.Integer()
    created_by_user = fields.Nested(UserSchema)



