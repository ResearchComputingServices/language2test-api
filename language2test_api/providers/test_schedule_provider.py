from language2test_api.extensions import db, ma
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.student_class import StudentClass
from language2test_api.models.test import Test
from language2test_api.models.test_session import TestSession
from datetime import datetime
from datetime import timezone


class TestScheduleProvider(BaseProvider):

    def get_schedule(self, data, user_id):
        tests_schedule = []

        start_datetime = datetime.strptime(data.get('start_datetime'), '%Y-%m-%dT%H:%M:%S.%fZ')
        end_datetime = datetime.strptime(data.get('end_datetime'), '%Y-%m-%dT%H:%M:%S.%fZ')


        # Retrieve all student classes of the user_id
        user_student_classes = db.session.execute('SELECT * FROM student_student_class WHERE student_id = :val',
                                                  {'val': user_id})
        for item_sc in user_student_classes:
            student_class_id = item_sc['student_class_id']
            student_class = StudentClass.query.filter_by(id=student_class_id).first()

            # Retrieve all test assignation in the student_class
            student_class_test_assignations = db.session.execute(
                'SELECT * FROM test_assignation_student_class WHERE student_class_id = :val', {'val': student_class_id})

            for item_ta in student_class_test_assignations:
                test_assignation_id = item_ta['test_assignation_id']
                test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

                if test_assignation.start_datetime >= start_datetime and test_assignation.end_datetime <= end_datetime:

                    info_schedule = {}
                    test_id = test_assignation.test_id

                    # We will query the test in test session to verify it is already taken.
                    test_session = TestSession.query.filter_by(test_id=test_id, user_id=user_id).first()
                    taken = False
                    if test_session:
                        taken = True

                    info_schedule['student_class_id'] = student_class_id
                    info_schedule['student_class_name'] = student_class.name
                    info_schedule['test_id'] = test_id
                    info_schedule['test_name'] = test_assignation.test.name
                    info_schedule['start_datetime'] = test_assignation.start_datetime
                    info_schedule['end_datetime'] = test_assignation.end_datetime
                    info_schedule['taken'] = taken
                    info_schedule['test_assignation_id'] = test_assignation_id

                    tests_schedule.append(info_schedule)

        return tests_schedule

