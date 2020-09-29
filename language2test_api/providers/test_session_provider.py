from language2test_api.extensions import db, ma
from language2test_api.providers.test_session_results_vocabulary_provider import TestSessionResultsVocabularyProvider
from language2test_api.providers.test_session_results_rc_provider import TestSessionResultsRCProvider
from language2test_api.providers.test_session_results_cloze_provider import TestSessionResultsClozeProvider
from language2test_api.providers.test_session_results_writing_provider import TestSessionResultsWritingProvider
from language2test_api.models.test_session import TestSession, TestSessionSchema

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
        db.session.add(test_session)
        return test_session

    def update(self, data, test_session):
        data = self.add_category_to_data(data)
        test_session.start_datetime = data.get('start_datetime')
        test_session.end_datetime = data.get('end_datetime')
        test_session.result_as_json = data.get('result_as_json')
        test_session.test_id = data.get('test_id')
        test_session.user_id = data.get('user_id')
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
        db.session.query(TestSession).filter(TestSession.id == data.get('id')).delete()