from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results import TestSessionBaseResults, TestSessionBaseResultsSchema

class TestSessionResultsWriting(TestSessionBaseResults):
    __tablename__ = 'test_session_results_writing'

    test_session_id = Column(db.Integer, ForeignKey('test_session.id'))
    answer = relationship("TestSessionResultsWritingAnswer", uselist=False, back_populates="results_writing")
    writing_id = Column(db.Integer, ForeignKey('writing.id'))

    def __init__(self, item):
        TestSessionBaseResults.__init__(self, item)
        self.test_session_id = item.get('test_session_id')
        self.writing_id = item.get('writing_id')

    def __repr__(self):
        return '<test_session_results_writing %r>' % self.id

from language2test_api.models.test_session_results_writing_answer import TestSessionResultsWritingAnswer, TestSessionResultsWritingAnswerSchema

class TestSessionResultsWritingSchema(TestSessionBaseResultsSchema):
    class Meta:
        model = TestSessionResultsWriting

    test_session_id = fields.Integer()
    answer = fields.Nested(TestSessionResultsWritingAnswerSchema, many=False)
    writing_id = fields.Integer()


