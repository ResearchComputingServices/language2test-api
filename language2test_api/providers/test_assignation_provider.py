from language2test_api.extensions import db, ma
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.student_class import StudentClass
from language2test_api.models.test import Test


class TestAssignationProvider(BaseProvider):

    def add(self, data):
        data['id'] = self.generate_id(field=TestAssignation.id)
        test_assignation = TestAssignation(data)

        for student_class in data.get('student_class'):
            student_class_db = StudentClass.query.filter_by(id=student_class.get('id')).first()
            if student_class_db:
                test_assignation.student_class.append(student_class_db)

        test = Test.query.filter_by(id=test_assignation.test_id).first()
        if test:
            test_assignation.test = test

        db.session.add(test_assignation)
        db.session.commit()
        return test_assignation


    def update(self, data, test_assignation):
        test_assignation.student_class = []
        test_assignation.start_datetime = data.get("start_datetime")
        test_assignation.end_datetime = data.get("end_datetime")

        for student_class in data.get('student_class'):
            student_class_db = StudentClass.query.filter_by(id=student_class.get('id')).first()
            if student_class_db:
                test_assignation.student_class.append(student_class_db)

        db.session.commit()
        return data





