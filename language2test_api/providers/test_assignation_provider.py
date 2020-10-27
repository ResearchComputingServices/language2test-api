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
                student_class_db.unremovable = True


        test = Test.query.filter_by(id=test_assignation.test_id).first()
        if test:
            test_assignation.test = test
            test.unremovable = True

        db.session.add(test_assignation)
        db.session.commit()
        return test_assignation


    def update(self, data, test_assignation):

        #Remove unremovable flag from student class
        for student_class in test_assignation.student_class:
            student_class_db = StudentClass.query.filter_by(id=student_class.id).first()
            student_class_db.unremovable = False


        test_assignation.student_class = []
        test_assignation.start_datetime = data.get("start_datetime")
        test_assignation.end_datetime = data.get("end_datetime")

        for student_class in data.get('student_class'):
            student_class_db = StudentClass.query.filter_by(id=student_class.get('id')).first()
            if student_class_db:
                test_assignation.student_class.append(student_class_db)
                student_class_db.unremovable = True

        db.session.commit()
        return test_assignation


    def delete(self, test_assignation):
        #Remove unremovable flag from student class
        for student_class in test_assignation.student_class:
            student_class_db = StudentClass.query.filter_by(id=student_class.id).first()
            student_class_db.unremovable = False

        # Remove unremovable flag from student class
        test = Test.query.filter_by(id=test_assignation.test_id).first()
        if test:
            test.unremovable = False

        db.session.delete(test_assignation)
        db.session.commit()


    def get_instructor_test_assignations(self, instructor_id):
        #1. Get all student classes for the instructor_id
        student_classes = StudentClass.query.filter_by(instructor_id=int(instructor_id)).all()
        test_assignation_id_list = []
        test_assignation_list = []

        #2 Get the test assignations for each student class
        for item_sc in student_classes:
            student_class_id = item_sc.id

            # Retrieve all test assignation in the student_class
            student_class_test_assignations = db.session.execute(
                'SELECT * FROM test_assignation_student_class WHERE student_class_id = :val', {'val': student_class_id})

            for item_ta in student_class_test_assignations:

                #Since a test assignation can contain multiple classes,
                #we need to avoid returning more than once the same test assignation
                test_assignation_id = item_ta['test_assignation_id']

                if test_assignation_id not in test_assignation_id_list:
                    test_assignation_id_list.append(test_assignation_id)
                    test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()
                    test_assignation_list.append(test_assignation)


        return test_assignation_list