from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test_session_results_vocabulary import TestSessionResultsVocabulary, TestSessionResultsVocabularySchema
from language2test_api.models.test_session_results_vocabulary_answers import TestSessionResultsVocabularyAnswers, TestSessionResultsVocabularyAnswersSchema
from language2test_api.models.vocabulary import Vocabulary, VocabularySchema
from language2test_api.models.vocabulary_option import VocabularyOption, VocabularyOptionSchema


class TestSessionResultsVocabularyProvider(BaseProvider):
    def add_results_vocabulary(self, data, test_session):
        if data.get('results_vocabulary') is not None:
            for index, data_results_vocabulary in enumerate(data.get('results_vocabulary')):
                data_results_vocabulary['id'] = self.generate_id(index, TestSessionResultsVocabulary.id)
                results_vocabulary = TestSessionResultsVocabulary(data_results_vocabulary)
                for index_data_answers, data_answers in enumerate(data_results_vocabulary.get('answers')):
                    data_answers['id'] = self.generate_id(index_data_answers, TestSessionResultsVocabularyAnswers.id)
                    answer = TestSessionResultsVocabularyAnswers(data_answers)
                    results_vocabulary.answers.append(answer)
                    #self.update_vocabulary_answered_correctly(answer.text, test_session.test_id, answer.vocabulary_id)
                    self.update_vocabulary_answered_correctly(answer)
                test_session.results_vocabulary.append(results_vocabulary)
        return test_session

    #def update_vocabulary_answered_correctly(self, text, test_id, vocabulary_id):
    def update_vocabulary_answered_correctly(self, answer):
        #Check if seen is true
        if answer.seen:
            #If attempted
            if  answer.attempted:
                #   Check if the answer is correct, in which case set the answered_correctly to 1, otherwise set the
                #   answered_correctly to 0.
                properties = Vocabulary.query.filter_by(id=int(answer.vocabulary_id)).first()
                correct_word = properties.options[properties.correct - 1]
                if correct_word.text == answer.text:
                    # Correct
                    answer.answered_correctly = 1
                else:
                    # Incorrect
                    answer.answered_correctly = 0
            else:
                #Seen is true and attempted is false, in which case set the answered_correctly to 0.
                answer.answered_correctly = 0
        #For seen=false answer is None (if not seen, attempted is false too)
        return

    def update_results_vocabulary(self, data, test_session):
        test_session.results_vocabulary = []
        if data.get('results_vocabulary') is not None:
            for index, data_results_vocabulary in enumerate(data.get('results_vocabulary')):
                data_results_vocabulary['id'] = self.generate_id(index, TestSessionResultsVocabulary.id)
                results_vocabulary = TestSessionResultsVocabulary(data_results_vocabulary)
                for index_data_answers, data_answers in enumerate(data_results_vocabulary.get('answers')):
                    data_answers['id'] = self.generate_id(index_data_answers, TestSessionResultsVocabularyAnswers.id)
                    answers = TestSessionResultsVocabularyAnswers(data_answers)
                    results_vocabulary.answers.append(answers)
                test_session.results_vocabulary.append(results_vocabulary)
        return test_session

    def delete_results_vocabulary(self, data, test_session):
        for results_vocabulary in test_session.results_vocabulary:
            for answer in results_vocabulary.answers:
                db.session.query(TestSessionResultsVocabularyAnswers).filter(
                    TestSessionResultsVocabularyAnswers.id == answer.id).delete()
            db.session.query(TestSessionResultsVocabulary).filter(
                TestSessionResultsVocabulary.id == results_vocabulary.id).delete()
        return test_session
