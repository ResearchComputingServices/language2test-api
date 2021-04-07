from language2test_api.extensions import db, ma
from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.models.test_session_base_results import TestSessionBaseResults, TestSessionBaseResultsSchema

class TestSessionResultsCloze(TestSessionBaseResults):
    __tablename__ = 'test_session_results_cloze'

    test_session_id = Column(db.Integer, ForeignKey('test_session.id'))
    answers = relationship("TestSessionResultsClozeAnswers", back_populates="results_cloze")
    cloze_id = Column(db.Integer, ForeignKey('cloze.id'))

    def __init__(self, item):
        TestSessionBaseResults.__init__(self, item)
        self.test_session_id = item.get('test_session_id')
        self.cloze_id = item.get('cloze_id')

    def __repr__(self):
        return '<test_session_results_cloze %r>' % self.id

from language2test_api.models.test_session_results_cloze_answers import TestSessionResultsClozeAnswers, TestSessionResultsClozeAnswersSchema

class TestSessionResultsClozeSchema(TestSessionBaseResultsSchema):
    class Meta:
        model = TestSessionResultsCloze

    test_session_id = fields.Integer()
    answers = fields.Nested(TestSessionResultsClozeAnswersSchema, many=True)
    cloze_id = fields.Integer()

