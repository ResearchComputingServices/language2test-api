from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema

class TestSessionBaseResultsAnswers(BaseTextModel):
    __abstract__ = True

    seen = db.Column(db.Boolean())
    attempted = db.Column(db.Boolean())
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    answered_correctly = db.Column(db.Integer())

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.seen = item.get('seen', False)
        self.attempted = item.get('attempted', False)
        self.start_time = item.get('start_time')
        self.end_time = item.get('end_time')
        self.answered_correctly = item.get('answered_correctly')

    def __repr__(self):
        return '<test_session_base_results_answers %r>' % self.id

class TestSessionBaseResultsAnswersSchema(BaseTextModelSchema):
    seen = fields.Boolean()
    attempted = fields.Boolean()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    answered_correctly = fields.Integer()





