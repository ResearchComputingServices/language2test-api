from datetime import datetime
from language2test_api.extensions import oidc
from flask import request
from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.role import Role, RoleSchema
from language2test_api.models.user import User, UserSchema
from language2test_api.models.user_field import UserField, UserFieldSchema
from language2test_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from language2test_api.models.user_field_type import UserFieldType, UserFieldTypeSchema
from language2test_api.models.student_class import StudentClass
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.models.test import Test
from language2test_api.models.user_field import UserField


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
        user.agree_to_participate = data.get('agree_to_participate')
        if 'roles' in data and data.get('roles'):
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

    def get_authenticated_user(self):
        auth = request.headers.get('Authorization')
        auth_fragments = auth.split(' ')
        token = auth_fragments[1]
        user_info = oidc.user_getinfo(['preferred_username', 'given_name', 'family_name'], token)
        username = user_info['preferred_username']

        # 2 Retrieve user information
        user = User.query.filter_by(name=username).first()

        return user

    def has_role(self, user, query_role):
        for role in user.roles:
            if query_role == role.name:
                return True

        return False



    def hide_roles(self, users):
        for user in users:
            user.roles = []


    def get_demographic_fields(self, user_id, start_datetime_rq, end_datetime_rq):

        demographic_fields =[]
        names = []
        user_tests =[]

        query_start_datetime = datetime.strptime(start_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')
        query_end_datetime = datetime.strptime(end_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')

        # Retrieve all student classes of the user_id
        user_student_classes = db.session.execute('SELECT * FROM student_student_class WHERE student_id = :val',
                                                  {'val': user_id})
        for item_sc in user_student_classes:
            student_class_id = item_sc['student_class_id']

            # Retrieve all test assignation in the student_class
            student_class_test_assignations = db.session.execute(
                'SELECT * FROM test_assignation_student_class WHERE student_class_id = :val', {'val': student_class_id})

            #Retrieve all tests
            for item_ta in student_class_test_assignations:
                test_assignation_id = item_ta['test_assignation_id']
                test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

                if not ((test_assignation.end_datetime <= query_start_datetime) or (
                        test_assignation.start_datetime >= query_end_datetime)):

                   test_id = test_assignation.test_id
                   if test_id not in user_tests:
                        user_tests.append(test_id)
                        test = Test.query.filter_by(id=test_id).first()


                        for user_field_category in test.test_user_field_category:
                            #Since a user field can be repeated in a multiple test, we avoid querying.
                            if user_field_category.name not in names:
                                names.append(user_field_category.name)
                                demographic_fields.append(user_field_category)

                                #Check if the user_field has been already answered
                                #user_field_with_answer = UserField.query.filter_by(name=user_field_category.name, user_id=user_id).first()
                                #if user_field_with_answer:
                                #    demographic_fields.append(user_field_with_answer)
                                #else:
                                #    demographic_fields.append(user_field_category)

        return demographic_fields


