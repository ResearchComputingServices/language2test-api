from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test_session_results_writing import TestSessionResultsWriting, TestSessionResultsWritingSchema
from language2test_api.models.test_session_results_writing_answer import TestSessionResultsWritingAnswer, TestSessionResultsWritingAnswerSchema
from language2test_api.models.writing import  Writing

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
                writing = Writing.query.filter_by(id=data_results_writing['writing_id']).first()
                if writing:
                    writing.unremovable = True  # Update flags: unremovable and immutable from the RC
                    writing.immutable = True
                test_session.results_writing.append(results_writing)
        return test_session

    def update_results_writing(self, data, test_session):
        # Need to check if generate id is correctly working
        # Uncomment the following line once the id are properly generated.
        #test_session.results_writing = []
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
            writing = Writing.query.filter_by(id=results_writing.writing_id).first()
            if writing:  # Update immutable
                writing.immutable = False


        for results_writing in test_session.results_writing:
            db.session.query(TestSessionResultsWritingAnswer).filter(
                TestSessionResultsWritingAnswer.results_writing_id == results_writing.id).delete()
            db.session.query(TestSessionResultsWriting).filter(
                TestSessionResultsWriting.id == results_writing.id).delete()
        return test_session
