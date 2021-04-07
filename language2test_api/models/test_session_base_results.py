from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema

class TestSessionBaseResults(BaseTextModel):
    __abstract__ = True

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.start = item.get('start')
        self.end = item.get('end')

    def __repr__(self):
        return '<test_session_base_results %r>' % self.id

class TestSessionBaseResultsSchema(BaseTextModelSchema):
    start = fields.DateTime()
    end = fields.DateTime()




