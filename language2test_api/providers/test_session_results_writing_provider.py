from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test_session_results_writing import TestSessionResultsWriting, TestSessionResultsWritingSchema
from language2test_api.models.test_session_results_writing_answer import TestSessionResultsWritingAnswer, TestSessionResultsWritingAnswerSchema

class TestSessionResultsWritingProvider(BaseProvider):
    def add_results_writing(self, data, test_session):
        if data.get('results_writing') is not None:
            for index, data_results_writing in enumerate(data.get('results_writing')):
                data_results_writing['id'] = self.generate_id(index, TestSessionResultsWriting.id)
                results_writing = TestSessionResultsWriting(data_results_writing)
                data_results_writing_answer = data_results_writing.get('answer')
                data_results_writing_answer['id'] = self.generate_id(index, TestSessionResultsWritingAnswer.id)
                results_writing_answer = TestSessionResultsWritingAnswer(data_results_writing_answer)
                results_writing_answer.results_writing_id = results_writing.id
                results_writing.answer = TestSessionResultsWritingAnswer(data_results_writing_answer)
                test_session.results_writing.append(results_writing)
        return test_session

    def update_results_writing(self, data, test_session):
        test_session.results_writing = []
        if data.get('results_writing') is not None:
            for index, data_results_writing in enumerate(data.get('results_writing')):
                data_results_writing['id'] = self.generate_id(index, TestSessionResultsWriting.id)
                results_writing = TestSessionResultsWriting(data_results_writing)
                data_results_writing_answer = data_results_writing.get('answer')
                data_results_writing_answer['id'] = self.generate_id(index, TestSessionResultsWritingAnswer.id)
                results_writing_answer = TestSessionResultsWritingAnswer(data_results_writing_answer)
                results_writing_answer.results_writing_id = results_writing.id
                results_writing.answer = TestSessionResultsWritingAnswer(data_results_writing_answer)
                test_session.results_writing.append(results_writing)
        return test_session

    def delete_results_writing(self, data, test_session):
        for results_writing in test_session.results_writing:
            db.session.query(TestSessionResultsWritingAnswer).filter(
                TestSessionResultsWritingAnswer.results_writing_id == results_writing.id).delete()
            db.session.query(TestSessionResultsWriting).filter(
                TestSessionResultsWriting.id == results_writing.id).delete()
        return test_session
