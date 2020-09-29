from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.extensions import db, ma

class BaseTextModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String())

    def __init__(self, item):
        self.id = item.get('id')
        self.text = item.get('text')

    def __repr__(self):
        return '<base_model %r>' % self.id

class BaseTextModelSchema(ma.ModelSchema):
    id = fields.Integer(dump_only=True)
    text = fields.String()


