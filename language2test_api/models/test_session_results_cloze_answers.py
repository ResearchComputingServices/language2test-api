from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma
from language2test_api.models.test_session_base_results_answers import TestSessionBaseResultsAnswers, TestSessionBaseResultsAnswersSchema

class TestSessionResultsClozeAnswers(TestSessionBaseResultsAnswers):
    __tablename__ = 'test_session_results_cloze_answers'

    results_cloze_id = Column(db.Integer, ForeignKey('test_session_results_cloze.id'))
    results_cloze = relationship("TestSessionResultsCloze", back_populates="answers")
    cloze_question_id = Column(db.Integer, ForeignKey('cloze_question.id'))

    def __init__(self, item):
        TestSessionBaseResultsAnswers.__init__(self, item)
        self.results_cloze_id = item.get('results_cloze_id')
        self.cloze_question_id = item.get('cloze_question_id')

    def __repr__(self):
        return '<test_session_results_cloze_answers %r>' % self.id

class TestSessionResultsClozeAnswersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TestSessionResultsClozeAnswers

    results_cloze_id = fields.Integer()
    cloze_question_id = fields.Integer()

