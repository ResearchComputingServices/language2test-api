from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.cloze_question_pending_typed import ClozeQuestionPendingTyped, ClozeQuestionPendingTypedSchema

class ClozeQuestionPendingTypedProvider(BaseProvider):
    def exist(self, text, cloze_question_id):
        query = ClozeQuestionPendingTyped.query
        query = query.filter(ClozeQuestionPendingTyped.cloze_question_id == cloze_question_id)
        query = query.filter(ClozeQuestionPendingTyped.text == text).first()
        return query != None

    def add(self, text, cloze_question_id):
        data = {}
        data['id'] = self.generate_id(field=ClozeQuestionPendingTyped.id)
        data['text'] = text
        data['cloze_question_id'] = cloze_question_id
        item = ClozeQuestionPendingTyped(data)
        db.session.add(item)
        db.session.commit()