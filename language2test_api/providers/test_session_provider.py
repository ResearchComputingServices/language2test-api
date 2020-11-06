from language2test_api.extensions import db, ma
from language2test_api.providers.test_session_results_vocabulary_provider import TestSessionResultsVocabularyProvider
from language2test_api.providers.test_session_results_rc_provider import TestSessionResultsRCProvider
from language2test_api.providers.test_session_results_cloze_provider import TestSessionResultsClozeProvider
from language2test_api.providers.test_session_results_writing_provider import TestSessionResultsWritingProvider
from language2test_api.models.test_session import TestSession, TestSessionSchema
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.models.test import Test
from sqlalchemy.sql import text

class TestSessionProvider(TestSessionResultsVocabularyProvider,
                          TestSessionResultsRCProvider,
                          TestSessionResultsClozeProvider,
                          TestSessionResultsWritingProvider):
    def __init__(self):
        super().__init__()

    def add(self, data):
        test_session = TestSession(data)
        test_session = self.add_results_vocabulary(data, test_session)
        test_session = self.add_results_rc(data, test_session)
        test_session = self.add_results_cloze(data, test_session)
        test_session = self.add_results_writing(data, test_session)
        if test_session.test_id is not None:
            test = Test.query.filter_by(id=test_session.test_id).first()
            if test:
                test.immutable = True
                test.unremovable = True
        db.session.add(test_session)
        return test_session

    def update(self, data, test_session):
        data = self.add_category_to_data(data)
        test_session.start_datetime = data.get('start_datetime')
        test_session.end_datetime = data.get('end_datetime')
        test_session.result_as_json = data.get('result_as_json')
        data_test = data.get('test')
        test_session.test_id = data_test['id']
        data_user = data.get('user')
        test_session.user_id = data_user['id']
        test_session = self.update_results_vocabulary(data, test_session)
        test_session = self.update_results_rc(data, test_session)
        test_session = self.update_results_cloze(data, test_session)
        test_session = self.update_results_writing(data, test_session)
        db.session.commit()
        return test_session

    def delete(self, data, test_session):
        test_session = self.delete_results_vocabulary(data, test_session)
        test_session = self.delete_results_rc(data, test_session)
        test_session = self.delete_results_cloze(data, test_session)
        self.delete_results_writing(data, test_session)
        if test_session.test_id is not None:
            test = Test.query.filter_by(id=test_session.test_id).first()
            if test:
                test.immutable = False
                test.unremovable = False
        db.session.query(TestSession).filter(TestSession.id == data.get('id')).delete()


    def get_test_sessions_for_test_assignation(self, test_assignation_id, offset, limit, column, order):

        test_sessions = []
        test_sessions_ids = []

        #Query test_assignation to retrieve test_id
        test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

        if test_assignation:
            #Get all test_sessions that include the test_id
            test_sessions_with_test_id = TestSession.query.filter_by(test_id=test_assignation.test_id).all()

            #test_sessions_per_test_id_2    Use a joint?
            #users = users.join(User.roles).filter(Role.id.in_(role.id for role in roles))

            for test_session in test_sessions_with_test_id:

                #Test session created_datetime should fall in test_assignation datetime period to take the test
                if test_session.created_datetime>= test_assignation.start_datetime and test_session.created_datetime<= test_assignation.end_datetime:

                    #Since the same test can be assigned to multiple test assignations
                    #Check if the user that created the test session is in at least one class assigned in the test assignation
                    student_classes_with_user = db.session.execute('SELECT * FROM student_student_class WHERE student_id = :val', {'val': test_session.user_id})

                    added = False
                    for item_sc in student_classes_with_user:
                        student_class_id = item_sc['student_class_id']

                        for assignation_class in test_assignation.student_class:
                            if student_class_id == assignation_class.id:
                                 test_sessions_ids.append(test_session.id)
                                 added = True
                                 break

                        if added:
                           break

            p = column + ' ' + order


            # Keep this for now for debugging purposes (just to verify that is really filtering)
            #query = TestSession.query.filter(TestSession.id.in_(test_sessions_ids))
            #results1 = query.all()

            #Query TestSession with the list of test sessions
            #This query allow us to paginate and order a subset

            if limit and offset:
                limit = int(limit)
                offset = int(offset)
                page = int(offset / limit) + 1
                test_sessions = TestSession.query.filter(TestSession.id.in_(test_sessions_ids)).order_by(text(p)).paginate(page=page,per_page=limit,error_out=False).items
            else:
                test_sessions = TestSession.query.filter(TestSession.id.in_(test_sessions_ids)).order_by(text(p)).all()

        return test_sessions

    def get_test_sessions_for_test_assignation_count(self, test_assignation_id):

        test_sessions = []
        test_sessions_ids = []

        # Query test_assignation to retrieve test_id
        test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

        if test_assignation:
            # Get all test_sessions that include the test_id
            test_sessions_with_test_id = TestSession.query.filter_by(test_id=test_assignation.test_id).all()

            # test_sessions_per_test_id_2    Use a joint?
            # users = users.join(User.roles).filter(Role.id.in_(role.id for role in roles))

            for test_session in test_sessions_with_test_id:

                # Test session created_datetime should fall in test_assignation datetime period to take the test
                if test_session.created_datetime >= test_assignation.start_datetime and test_session.created_datetime <= test_assignation.end_datetime:

                    # Since the same test can be assigned to multiple test assignations
                    # Check if the user that created the test session is in at least one class assigned in the test assignation
                    student_classes_with_user = db.session.execute(
                        'SELECT * FROM student_student_class WHERE student_id = :val', {'val': test_session.user_id})

                    added = False
                    for item_sc in student_classes_with_user:
                        student_class_id = item_sc['student_class_id']

                        for assignation_class in test_assignation.student_class:
                            if student_class_id == assignation_class.id:
                                test_sessions_ids.append(test_session.id)
                                added = True
                                break

                        if added:
                            break

        test_sessions_ids = list(set(test_sessions_ids))
        dict = {"count": len(test_sessions_ids)}

        return dict

    def get_test_sessions_for_test_assignation(self, test_assignation_id):

        test_sessions = []
        test_sessions_ids = []

        # Query test_assignation to retrieve test_id
        test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

        if test_assignation:
            # Get all test_sessions that include the test_id
            test_sessions_with_test_id = TestSession.query.filter_by(test_id=test_assignation.test_id).all()

            # test_sessions_per_test_id_2    Use a joint?
            # users = users.join(User.roles).filter(Role.id.in_(role.id for role in roles))

            for test_session in test_sessions_with_test_id:

                # Test session created_datetime should fall in test_assignation datetime period to take the test
                if test_session.created_datetime >= test_assignation.start_datetime and test_session.created_datetime <= test_assignation.end_datetime:

                    # Since the same test can be assigned to multiple test assignations
                    # Check if the user that created the test session is in at least one class assigned in the test assignation
                    student_classes_with_user = db.session.execute(
                        'SELECT * FROM student_student_class WHERE student_id = :val', {'val': test_session.user_id})

                    added = False
                    for item_sc in student_classes_with_user:
                        student_class_id = item_sc['student_class_id']

                        for assignation_class in test_assignation.student_class:
                            if student_class_id == assignation_class.id:
                                test_sessions_ids.append(test_session.id)
                                added = True
                                break

                        if added:
                            break

            # Query TestSession with the list of test sessions
            # This query allow us to paginate and order a subset

            test_sessions = TestSession.query.filter(TestSession.id.in_(test_sessions_ids)).all()

            # Do the export here

        return test_sessions