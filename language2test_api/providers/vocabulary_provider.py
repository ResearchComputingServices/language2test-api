from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.vocabulary import Vocabulary, VocabularySchema
from language2test_api.models.vocabulary_option import VocabularyOption, VocabularyOptionSchema

class VocabularyProvider(BaseProvider):
    def add(self, data):
        data = self.add_category_to_data(data)
        data['id'] = self.generate_id(field=Vocabulary.id)
        vocabulary = Vocabulary(data)
        db.session.add(vocabulary)
        for option in data.get('options'):
            vocabulary_option = VocabularyOption(option)
            vocabulary.options.append(vocabulary_option)
        db.session.commit()
        return vocabulary

    def delete(self, data, vocabulary):
        for option in vocabulary.options:
            db.session.query(VocabularyOption).filter(VocabularyOption.id == option.id).delete()
        db.session.query(Vocabulary).filter(Vocabulary.word == data.get('word')).delete()

    def update(self, data, vocabulary):
        data = self.add_category_to_data(data)
        vocabulary.test_category_id = data.get("test_category_id")
        vocabulary.correct = data.get("correct")
        vocabulary.time_limit = data.get("time_limit")
        vocabulary.options = []
        for option in data.get('options'):
            vocabulary_option = VocabularyOption(option)
            vocabulary.options.append(vocabulary_option)
        db.session.commit()