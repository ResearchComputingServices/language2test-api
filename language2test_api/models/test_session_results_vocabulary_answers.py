from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results_answers import TestSessionBaseResultsAnswers, TestSessionBaseResultsAnswersSchema

class TestSessionResultsVocabularyAnswers(TestSessionBaseResultsAnswers):
    __tablename__ = 'test_session_results_vocabulary_answers'

    results_vocabulary_id = Column(db.Integer, ForeignKey('test_session_results_vocabulary.id'))
    results_vocabulary = relationship("TestSessionResultsVocabulary", back_populates="answers")
    vocabulary_id = Column(db.Integer, ForeignKey('vocabulary.id'))

    def __init__(self, item):
        TestSessionBaseResultsAnswers.__init__(self, item)
        self.results_vocabulary_id = item.get('results_vocabulary_id')
        self.vocabulary_id = item.get('vocabulary_id')

    def __repr__(self):
        return '<test_session_results_vocabulary_answers %r>' % self.id

class TestSessionResultsVocabularyAnswersSchema(TestSessionBaseResultsAnswersSchema):
    class Meta:
        model = TestSessionResultsVocabularyAnswers

    results_vocabulary_id = fields.Integer()
    vocabulary_id = fields.Integer()

