from marshmallow import Schema, fields, ValidationError, pre_load
from language2test_api.models.base_model import BaseModel, BaseModelSchema
from language2test_api.extensions import db, ma
from sqlalchemy.orm import relationship

role_authorization = db.Table('role_authorization',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('authorization_id', db.Integer, db.ForeignKey('authorization.id'), primary_key=True)
)

class Role(BaseModel):
    __tablename__ = 'role'

    immutable =  db.Column(db.Boolean, default=False)
    authorizations = relationship("Authorization", secondary=role_authorization)

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
    authorizations = fields.Nested(AuthorizationSchema, many=True)

