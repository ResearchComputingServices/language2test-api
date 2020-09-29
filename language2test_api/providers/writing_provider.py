from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.writing import Writing, WritingSchema

class WritingProvider(BaseProvider):
    def add(self, data):
        data = self.add_category_to_data(data)
        data['id'] = self.generate_id(field=Writing.id)
        writing = Writing(data)
        db.session.add(writing)
        db.session.commit()
        return writing

    def delete(self, data, writing):
        db.session.query(Writing).filter(Writing.name == data.get('name')).delete()

    def update(self, data, writing):
        data = self.add_category_to_data(data)
        writing.test_category_id = data.get("test_category_id")
        writing.question = data.get("question")
        writing.word_limit = data.get("word_limit")
        writing.time_limit = data.get("time_limit")
        writing.type = data.get("type")
        writing.filename = data.get("filename")
        db.session.commit()