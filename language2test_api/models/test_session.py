import datetime
from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.user import User, UserSchema
from language2test_api.models.test import Test, TestSchema
from language2test_api.models.test_session_results_vocabulary import TestSessionResultsVocabulary, TestSessionResultsVocabularySchema
from language2test_api.models.test_session_results_rc import TestSessionResultsRC, TestSessionResultsRCSchema
from language2test_api.models.test_session_results_cloze import TestSessionResultsCloze, TestSessionResultsClozeSchema
from language2test_api.models.test_session_results_writing import TestSessionResultsWriting, TestSessionResultsWritingSchema
from language2test_api.models.base_model import BaseModel, BaseModelSchema

class TestSession(BaseModel):
    __tablename__ = 'test_session'

    user_id = db.Column(db.Integer(), ForeignKey('user.id'))
    user = relationship("User")
    created_datetime = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    start_datetime = db.Column(db.DateTime())
    end_datetime = db.Column(db.DateTime())
    result_as_json = db.Column(db.String())
    test_id = db.Column(db.Integer(), ForeignKey('test.id'))
    test = relationship("Test")
    grade = db.Column(db.Float())
    max_grade = db.Column(db.Float())
    results_vocabulary = relationship(TestSessionResultsVocabulary, backref="results_vocabulary")
    results_rc = relationship(TestSessionResultsRC, backref="results_rc")
    results_cloze = relationship("TestSessionResultsCloze", backref="test_session")
    results_writing = relationship("TestSessionResultsWriting", backref="test_session")

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.user_id = item.get('user_id')
        self.result_as_json = item.get('result_as_json')
        self.start_datetime = item.get('start_datetime')
        self.end_datetime = item.get('end_datetime')
        self.test_id = item.get('test_id')
        self.grade = item.get('grade')
        self.max_grade = item.get('max_grade')


    def __repr__(self):
        return '<test_session %s>' % (str(self.id))

class TestSessionSchema(BaseModelSchema):
    class Meta:
        model = TestSession

    user_id = fields.String()
    user = fields.Nested(UserSchema)
    created_datetime = fields.DateTime()
    result_as_json = fields.String()
    start_datetime = fields.DateTime()
    end_datetime = fields.DateTime()
    test = fields.Nested(TestSchema)
    test_id = fields.Integer()
    grade = fields.Float()
    max_grade = fields.Float()
    results_vocabulary = fields.Nested(TestSessionResultsVocabularySchema, many=True)
    results_rc = fields.Nested(TestSessionResultsRCSchema, many=True)
    results_cloze = fields.Nested(TestSessionResultsClozeSchema, many=True)
    results_writing = fields.Nested(TestSessionResultsWritingSchema, many=True)

