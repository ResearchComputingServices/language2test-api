from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.role import Role, RoleSchema
from language2test_api.models.user import User, UserSchema
from language2test_api.models.user_field import UserField, UserFieldSchema
from language2test_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from language2test_api.models.user_field_type import UserFieldType, UserFieldTypeSchema
from language2test_api.models.test_session import TestSession, TestSessionSchema

class UserProvider(BaseProvider):
    def add(self, data):
        data['id'] = self.generate_id(field=User.id)
        user = User(data)
        for roles in data.get('roles'):
            role = Role.query.filter_by(name=roles.get('name')).first()
            if role:
                user.roles.append(role)
        db.session.add(user)
        for field in data.get('fields'):
            user_field_type = 'text'
            user_field_category = UserFieldCategory.query.filter_by(name=field.get('name')).first()
            if user_field_category:
                user_field_type = user_field_category.user_field_type.name
            field['type'] = user_field_type
            user_field = UserField(field)
            user_field.user_id = user.id
            user.fields.append(user_field)
        db.session.commit()
        return user

    def update(self, data, user):
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.roles = []
        for role_item in data.get('roles'):
            role = Role.query.filter_by(name=role_item.get('name')).first()
            if role:
                user.roles.append(role)

        for field in user.fields:
            db.session.query(UserField).filter(UserField.id == field.id).delete()

        for field in data.get('fields'):
            user_field_type = 'text'
            user_field_category = UserFieldCategory.query.filter_by(name=field.get('name')).first()
            if user_field_category:
                user_field_type = user_field_category.user_field_type.name
            field['type'] = user_field_type
            user_field = UserField(field)
            user_field.user_id= user.id
            user.fields.append(user_field)

        return user

    def delete(self, data):
        user = User.query.filter_by(id=data.get('id')).first()
        if not user:
            user = User.query.filter_by(name=data.get('name')).first()
        if user:
            for field in user.fields:
                db.session.query(UserField).filter(UserField.id == field.id).delete()
        return user

