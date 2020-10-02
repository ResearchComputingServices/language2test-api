from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test_session_results_cloze import TestSessionResultsCloze, TestSessionResultsClozeSchema
from language2test_api.models.test_session_results_cloze_answers import TestSessionResultsClozeAnswers, TestSessionResultsClozeAnswersSchema
from language2test_api.providers.test_provider import TestProvider
from language2test_api.models.cloze_question import ClozeQuestion
from language2test_api.providers.cloze_question_correctly_typed_provider import ClozeQuestionCorrectlyTypedProvider
from language2test_api.providers.cloze_question_incorrectly_typed_provider import ClozeQuestionIncorrectlyTypedProvider
from language2test_api.providers.cloze_question_pending_typed_provider import ClozeQuestionPendingTypedProvider
from language2test_api.models.cloze import Cloze

test_provider = TestProvider()
correctly_typed_provider = ClozeQuestionCorrectlyTypedProvider()
incorrectly_typed_provider = ClozeQuestionIncorrectlyTypedProvider()
pending_typed_provider = ClozeQuestionPendingTypedProvider()

class TestSessionResultsClozeProvider(BaseProvider):
    def add_results_cloze(self, data, test_session):
        if data.get('results_cloze') is not None:
            for index, data_results_cloze in enumerate(data.get('results_cloze')):
                data_results_cloze['id'] = self.generate_id(index, TestSessionResultsCloze.id)
                results_cloze = TestSessionResultsCloze(data_results_cloze)
                for index_data_answers, data_answers in enumerate(data_results_cloze.get('answers')):
                    data_answers['id'] = self.generate_id(index_data_answers, TestSessionResultsClozeAnswers.id)
                    answer = TestSessionResultsClozeAnswers(data_answers)
                    results_cloze.answers.append(answer)
                    self.add_typed_text_to_pending_list(answer.text, test_session.test_id,
                                                        results_cloze.cloze_id, answer.cloze_question_id)
                    self.update_cloze_answered_correctly(answer, test_session.test_id, results_cloze.cloze_id)
                cloze = Cloze.query.filter_by(id=results_cloze.cloze_id).first()
                if cloze:
                    cloze.unremovable = True  # Update flags: unremovable and immutable from the RC
                    cloze.immutable = True
                test_session.results_cloze.append(results_cloze)
        return test_session

    def add_typed_text_to_pending_list(self, text, test_id, cloze_id, cloze_question_id):
        # Check if text has been typed instead of selected from a list. If was not typed or was neither selected
        # nor typed, then return and do nothing.
        found = test_provider.exist(text, test_id, cloze_id, cloze_question_id)
        if found or text is None:
            return

        # Check if text was found in the correct, incorrect or pending list. If yes, then return and do nothing.
        typed_providers = [correctly_typed_provider, incorrectly_typed_provider, pending_typed_provider]
        for index, typed_provider in enumerate(typed_providers):
            found = typed_provider.exist(text, cloze_question_id)
            if found:
                return

        # Add the text to the pending list
        pending_typed_provider.add(text, cloze_question_id)

    def update_cloze_answered_correctly(self, answer, test_id, cloze_id):
        if answer.seen:
            # If attempted
            if answer.attempted:
                # Check if text has been typed instead of selected from a list.
                typed = not(test_provider.exist(answer.text, test_id, cloze_id, answer.cloze_question_id))
                if typed:
                    # Check if is found inside the correct list, in which case set the answered_correctly to 1
                    correctly_typed = correctly_typed_provider.exist(answer.text,answer.cloze_question_id)
                    if correctly_typed:
                        answer.answered_correctly = 1
                    else:
                        incorrectly_typed = incorrectly_typed_provider.exist(answer.text,answer.cloze_question_id)
                        if incorrectly_typed:
                            answer.answered_correctly = 0
                    return
                else:
                    #Check if the answer is correct, in which case set the answered_correctly to 1, otherwise set the
                    #answered_correctly to 0.
                    properties = ClozeQuestion.query.filter_by(id=int(answer.cloze_question_id)).first()
                    correct_word = properties.options[properties.correct - 1]
                    if correct_word.text == answer.text:
                        # Correct
                        answer.answered_correctly = 1
                    else:
                        # Incorrect
                        answer.answered_correctly = 0
                    return
            else:
                # Seen is true and attempted is false, in which case set the answered_correctly to 0.
                answer.answered_correctly = 0
            # For seen=false answer is None (if not seen, attempted is false too)
        return


    def update_results_cloze(self, data, test_session):
        # Need to check if generate id is correctly working
        # Uncomment the following line once the id are properly generated.
        #test_session.results_cloze = []
        if data.get('results_cloze') is not None:
            for index, data_results_cloze in enumerate(data.get('results_cloze')):
                data_results_cloze['id'] = self.generate_id(index, TestSessionResultsCloze.id)
                results_cloze = TestSessionResultsCloze(data_results_cloze)
                for index_data_answers, data_answers in enumerate(data_results_cloze.get('answers')):
                    data_answers['id'] = self.generate_id(index_data_answers, TestSessionResultsClozeAnswers.id)
                    answer = TestSessionResultsClozeAnswers(data_answers)
                    results_cloze.answers.append(answer)
                test_session.results_cloze.append(results_cloze)
        return test_session

    def delete_results_cloze(self, data, test_session):
        for results_cloze in test_session.results_cloze:
            cloze = Cloze.query.filter_by(id=results_cloze.cloze_id).first()
            if cloze:
                cloze.immutable = False

            for answer in results_cloze.answers:
                db.session.query(TestSessionResultsClozeAnswers).filter(
                    TestSessionResultsClozeAnswers.id == answer.id).delete()
            db.session.query(TestSessionResultsCloze).filter(
                TestSessionResultsCloze.id == results_cloze.id).delete()
        return test_session
