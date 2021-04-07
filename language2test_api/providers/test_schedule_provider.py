from language2test_api.extensions import db, ma
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.student_class import StudentClass
from language2test_api.models.test import Test
from language2test_api.models.test_session import TestSession
from datetime import datetime


class TestScheduleProvider(BaseProvider):

    def get_test_taker_schedule(self, user_id, start_datetime_rq, end_datetime_rq):
        tests_schedule = []

        query_start_datetime = datetime.strptime(start_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')
        query_end_datetime = datetime.strptime(end_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')

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

                if not ((test_assignation.end_datetime <= query_start_datetime) or (
                        test_assignation.start_datetime >= query_end_datetime)):

                    info_schedule = {}
                    test_id = test_assignation.test_id

                    # We will query the test in test session to verify it is already taken.
                    test_sessions = TestSession.query.filter_by(test_id=test_id, user_id=user_id, class_id=student_class_id).all()
                    taken = False
                    for test_session in test_sessions:
                        if (test_session.created_datetime>=test_assignation.start_datetime and test_session.created_datetime<=test_assignation.end_datetime):
                            taken = True
                            break

                    info_schedule['student_class_id'] = student_class_id
                    info_schedule['student_class_name'] = student_class.display
                    info_schedule['test_id'] = test_id
                    info_schedule['test_name'] = test_assignation.test.name
                    info_schedule['start_datetime'] = test_assignation.start_datetime
                    info_schedule['end_datetime'] = test_assignation.end_datetime
                    info_schedule['taken'] = taken
                    info_schedule['test_assignation_id'] = test_assignation_id

                    tests_schedule.append(info_schedule)

        return tests_schedule



    def get_instructor_test_schedule(self, instructor_id, start_datetime_rq, end_datetime_rq):

        query_start_datetime = datetime.strptime(start_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')
        query_end_datetime = datetime.strptime(end_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')

        #Get all student classes for the instructor_id
        student_classes_for_instructor = StudentClass.query.filter_by(instructor_id=int(instructor_id)).all()
        test_assignations_id = []
        test_assignations = []

        # Get all the test assignations for all the student_classes
        for item_sc in student_classes_for_instructor:
            student_class_id = item_sc.id

            # Retrieve all test assignations that contain the student_class_id
            test_assignations_with_student_class = db.session.execute(
                'SELECT * FROM test_assignation_student_class WHERE student_class_id = :val', {'val': student_class_id})

            for item_ta in test_assignations_with_student_class:

                # Since a test assignation can contain multiple classes,
                # we need to avoid returning more than once the same test assignation
                test_assignation_id = item_ta['test_assignation_id']

                if test_assignation_id not in test_assignations_id:
                    test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

                    if not ((test_assignation.end_datetime <= query_start_datetime) or (
                            test_assignation.start_datetime >= query_end_datetime)):

                        test_assignations_id.append(test_assignation_id)
                        test_assignations.append(test_assignation)

        return test_assignations



