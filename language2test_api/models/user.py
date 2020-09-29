from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.role import Role, RoleSchema
from language2test_api.models.base_model import BaseModel, BaseModelSchema

user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(BaseModel):
    __tablename__ = 'user'

    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    roles = relationship("Role", secondary=user_role)
    fields = relationship("UserField", back_populates="user")

    def __init__(self, item):
        BaseModel.__init__(self, item)
        self.first_name = item.get('first_name')
        self.last_name = item.get('last_name')

    def __repr__(self):
        return '<user %r>' % self.name

from language2test_api.models.user_field import UserField, UserFieldSchema

class UserSchema(BaseModelSchema):
    class Meta:
        model = User

    first_name = fields.String()
    last_name = fields.String()
    roles = fields.Nested(RoleSchema, many=True)
    fields = fields.Nested(UserFieldSchema, many=True)