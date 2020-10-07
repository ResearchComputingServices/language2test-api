from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test_session_results_rc import TestSessionResultsRC, TestSessionResultsRCSchema
from language2test_api.models.test_session_results_rc_answers import TestSessionResultsRCAnswers, TestSessionResultsRCAnswersSchema
from language2test_api.models.rc import RCQuestion
from language2test_api.models.rc import RC, RCSchema

class TestSessionResultsRCProvider(BaseProvider):
    def add_results_rc(self, data, test_session):
        if data.get('results_rc') is not None:

            offset=0
            for index, data_results_rc in enumerate(data.get('results_rc')):
                data_results_rc['id'] = self.generate_id(index, TestSessionResultsRC.id)
                results_rc = TestSessionResultsRC(data_results_rc)

                for index_data_answers, data_answers in enumerate(data_results_rc.get('answers')):
                    #data_answers['id'] = self.generate_id(index_data_answers, TestSessionResultsRCAnswers.id)
                    data_answers['id'] = self.generate_id(offset, TestSessionResultsRCAnswers.id)
                    answer = TestSessionResultsRCAnswers(data_answers)
                    results_rc.answers.append(answer)
                    self.update_rc_answered_correctly(answer)
                    offset = offset + 1

                rc = RC.query.filter_by(id=results_rc.rc_id).first()
                if rc:
                    rc.unremovable = True  # Update flags: unremovable and immutable from the RC
                    rc.immutable = True
                test_session.results_rc.append(results_rc)
        return test_session

    def update_rc_answered_correctly(self, answer):
    # Check if seen is true
        if answer.seen:
            # If attempted
            if answer.attempted:
                #   Check if the answer is correct, in which case set the answered_correctly to 1, otherwise set the
                #   answered_correctly to 0.
                properties = RCQuestion.query.filter_by(id=int(answer.rc_question_id)).first()
                correct_answer = properties.options[properties.correct - 1]
                if correct_answer.text == answer.text:
                # Correct
                    answer.answered_correctly = 1
                else:
                    # Incorrect
                    answer.answered_correctly = 0
            else:
                # Seen is true and attempted is false, in which case set the answered_correctly to 0.
                answer.answered_correctly = 0
        # For seen=false answer is None (if not seen, attempted is false too)
        return


    def update_results_rc(self, data, test_session):



        #Set immutable to false from previous RC
        #for test_rc in test_session.results_rc:
        #    rc = RC.query.filter_by(id=test_rc.rc_id).first()
        #    if rc:
        #        rc.immutable = False

        #This update needs fixing.
        #Fields 'results_rc' doesn't exist.
        #Generate id needs fixing.

        #test_session.results_rc = []
        if data.get('results_rc') is not None:
            for index, data_results_rc in enumerate(data.get('results_rc')):
                data_results_rc['id'] = self.generate_id(index, TestSessionResultsRC.id)
                results_rc = TestSessionResultsRC(data_results_rc)
                for index_data_answers, data_answers in enumerate(data_results_rc.get('answers')):
                    data_answers['id'] = self.generate_id(index_data_answers, TestSessionResultsRCAnswers.id)
                    answers = TestSessionResultsRCAnswers(data_answers)
                    results_rc.answers.append(answers)
                rc = RC.query.filter_by(id=results_rc.rc_id).first()
                if rc:
                    rc.unremovable = True  # Update flags: unremovable and immutable from the RC
                    rc.immutable = True
                test_session.results_rc.append(results_rc)
        return test_session

    def delete_results_rc(self, data, test_session):

        for results_rc in test_session.results_rc:
            rc = RC.query.filter_by(id=results_rc.rc_id).first()
            if rc:  # Update immutable
                rc.immutable = False

            for answer in results_rc.answers:
                db.session.query(TestSessionResultsRCAnswers).filter(
                    TestSessionResultsRCAnswers.id == answer.id).delete()
            db.session.query(TestSessionResultsRC).filter(
                TestSessionResultsRC.id == results_rc.id).delete()
        return test_session
