from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results_answers import TestSessionBaseResultsAnswers, TestSessionBaseResultsAnswersSchema

class TestSessionResultsWritingAnswer(TestSessionBaseResultsAnswers):
    __tablename__ = 'test_session_results_writing_answers'

    results_writing_id = Column(db.Integer, ForeignKey('test_session_results_writing.id'))
    results_writing = relationship("TestSessionResultsWriting", back_populates="answer")

    def __init__(self, item):
        TestSessionBaseResultsAnswers.__init__(self, item)
        self.results_writing_id = item.get('results_writing_id')

    def __repr__(self):
        return '<test_session_results_writing_answers %r>' % self.id

class TestSessionResultsWritingAnswerSchema(TestSessionBaseResultsAnswersSchema):
    class Meta:
        model = TestSessionResultsWritingAnswer

    results_writing_id = fields.Integer()


