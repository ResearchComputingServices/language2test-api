from language2test_api.extensions import db, ma
from language2test_api.providers.test_session_results_vocabulary_provider import TestSessionResultsVocabularyProvider
from language2test_api.providers.test_session_results_rc_provider import TestSessionResultsRCProvider
from language2test_api.providers.test_session_results_cloze_provider import TestSessionResultsClozeProvider
from language2test_api.providers.test_session_results_writing_provider import TestSessionResultsWritingProvider
from language2test_api.models.test_session import TestSession, TestSessionSchema
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.models.test import Test

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


    def get_test_sessions_for_test_assignation(self, test_assignation_id):

        test_sessions_assignations = []

        #1. Query the test_assignation to retrieve the test_id
        test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

        if test_assignation:

            #2. Get all test_sessions that include the test_id belonging to the test assignation
            test_sessions_per_test_id = TestSession.query.filter_by(test_id=test_assignation.test_id).all()

            for test_session in test_sessions_per_test_id:

                # 3. The created_datetime in the test_session should fall in the test_assignation period of the test
                if test_session.created_datetime>= test_assignation.start_datetime and test_session.created_datetime<= test_assignation.end_datetime:

                    #4. Verify if the user that created the test session is in at least one class contained in the test assignation
                    user_student_classes = db.session.execute('SELECT * FROM student_student_class WHERE student_id = :val', {'val': test_session.user_id})

                    added = False
                    for item_sc in user_student_classes:
                        student_class_id = item_sc['student_class_id']

                        for assignation_class in test_assignation.student_class:
                            if student_class_id == assignation_class.id:
                                 test_sessions_assignations.append(test_session)
                                 added = True
                                 break

                        if added:
                           break

        return test_sessions_assignations

