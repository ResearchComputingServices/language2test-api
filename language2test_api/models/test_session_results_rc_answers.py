from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results_answers import TestSessionBaseResultsAnswers, TestSessionBaseResultsAnswersSchema

class TestSessionResultsRCAnswers(TestSessionBaseResultsAnswers):
    __tablename__ = 'test_session_results_rc_answers'

    results_rc_id = Column(db.Integer, ForeignKey('test_session_results_rc.id'))
    results_rc = relationship("TestSessionResultsRC", back_populates="answers")
    rc_question_id = Column(db.Integer, ForeignKey('rc_question.id'))

    def __init__(self, item):
        TestSessionBaseResultsAnswers.__init__(self, item)
        self.results_rc_id = item.get('results_rc_id')
        self.rc_question_id = item.get('rc_question_id')

    def __repr__(self):
        return '<test_session_results_rc_answers %r>' % self.id

class TestSessionResultsRCAnswersSchema(TestSessionBaseResultsAnswersSchema):
    class Meta:
        model = TestSessionResultsRCAnswers

    results_rc_id = fields.Integer()
    rc_question_id = fields.Integer()

