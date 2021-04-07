from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results import TestSessionBaseResults, TestSessionBaseResultsSchema

class TestSessionResultsVocabulary(TestSessionBaseResults):
    __tablename__ = 'test_session_results_vocabulary'

    test_session_id = Column(db.Integer, ForeignKey('test_session.id'))
    answers = relationship("TestSessionResultsVocabularyAnswers", back_populates="results_vocabulary")

    def __init__(self, item):
        TestSessionBaseResults.__init__(self, item)
        self.test_session_id = item.get('test_session_id')

    def __repr__(self):
        return '<test_session_results_vocabulary %r>' % self.id

from language2test_api.models.test_session_results_vocabulary_answers import TestSessionResultsVocabularyAnswers, TestSessionResultsVocabularyAnswersSchema

class TestSessionResultsVocabularySchema(TestSessionBaseResultsSchema):
    class Meta:
        model = TestSessionResultsVocabulary

    test_session_id = fields.Integer()
    answers = fields.Nested(TestSessionResultsVocabularyAnswersSchema, many=True)

