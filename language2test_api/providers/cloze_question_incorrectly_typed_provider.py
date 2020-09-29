from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.cloze_question_incorrectly_typed import ClozeQuestionIncorrectlyTyped, ClozeQuestionIncorrectlyTypedSchema

class ClozeQuestionIncorrectlyTypedProvider(BaseProvider):
    def exist(self, text, cloze_question_id):
        query = ClozeQuestionIncorrectlyTyped.query
        query = query.filter(ClozeQuestionIncorrectlyTyped.cloze_question_id == cloze_question_id)
        query = query.filter(ClozeQuestionIncorrectlyTyped.text == text).first()
        return query != None

    def add(self, text, cloze_question_id):
        data = {}
        data['id'] = self.generate_id(field=ClozeQuestionIncorrectlyTyped.id)
        data['text'] = text
        data['cloze_question_id'] = cloze_question_id
        item = ClozeQuestionIncorrectlyTyped(data)
        db.session.add(item)
        db.session.commit()