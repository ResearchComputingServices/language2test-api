from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results import TestSessionBaseResults, TestSessionBaseResultsSchema

class TestSessionResultsRC(TestSessionBaseResults):
    __tablename__ = 'test_session_results_rc'

    test_session_id = Column(db.Integer, ForeignKey('test_session.id'))
    answers = relationship("TestSessionResultsRCAnswers", back_populates="results_rc")
    rc_id = Column(db.Integer, ForeignKey('rc.id'))

    def __init__(self, item):
        TestSessionBaseResults.__init__(self, item)
        self.test_session_id = item.get('test_session_id')
        self.rc_id = item.get('rc_id')

    def __repr__(self):
        return '<test_session_results_rc %r>' % self.id

from language2test_api.models.test_session_results_rc_answers import TestSessionResultsRCAnswers, TestSessionResultsRCAnswersSchema

class TestSessionResultsRCSchema(TestSessionBaseResultsSchema):
    class Meta:
        model = TestSessionResultsRC

    test_session_id = fields.Integer()
    answers = fields.Nested(TestSessionResultsRCAnswersSchema, many=True)
    rc_id = fields.Integer()

