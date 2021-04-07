from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.models.base_model import BaseModel, BaseModelSchema
from language2test_api.extensions import db, ma
from sqlalchemy.orm import relationship

class Role(BaseModel):
    __tablename__ = 'role'

    immutable =  db.Column(db.Boolean, default=False)

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.immutable = item.get('immutable')

    def __repr__(self):
        return '<role %r>' % self.name

from language2test_api.models.authorization import Authorization, AuthorizationSchema

class RoleSchema(BaseModelSchema):
    class Meta:
        model = Role

    immutable = fields.Boolean()


