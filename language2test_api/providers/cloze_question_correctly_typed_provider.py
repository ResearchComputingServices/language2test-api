from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.cloze_question_correctly_typed import ClozeQuestionCorrectlyTyped, ClozeQuestionCorrectlyTypedSchema

class ClozeQuestionCorrectlyTypedProvider(BaseProvider):
    def exist(self, text, cloze_question_id):
        query = ClozeQuestionCorrectlyTyped.query
        query = query.filter(ClozeQuestionCorrectlyTyped.cloze_question_id == cloze_question_id)
        query = query.filter(ClozeQuestionCorrectlyTyped.text == text).first()
        return query != None

    def get(self, text, cloze_question_id):
        query = ClozeQuestionCorrectlyTyped.query
        query = query.filter(ClozeQuestionCorrectlyTyped.cloze_question_id == cloze_question_id)
        query = query.filter(ClozeQuestionCorrectlyTyped.text == text).first()
        return query

    def get_query(self, cloze_question_id):
        query = ClozeQuestionCorrectlyTyped.query
        query = query.filter(ClozeQuestionCorrectlyTyped.cloze_question_id == cloze_question_id).all()
        return query

    def add(self, text, cloze_question_id):
        data = {}
        data['id'] = self.generate_id(field=ClozeQuestionCorrectlyTyped.id)
        data['text'] = text
        data['cloze_question_id'] = cloze_question_id
        item = ClozeQuestionCorrectlyTyped(data)
        db.session.add(item)
        db.session.commit()




