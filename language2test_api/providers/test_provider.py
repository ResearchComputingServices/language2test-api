from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test import Test, TestSchema
from language2test_api.models.rc import RC, RCSchema
from language2test_api.models.cloze import Cloze, ClozeSchema
from language2test_api.models.writing import Writing, WritingSchema
from language2test_api.models.vocabulary import Vocabulary, VocabularySchema, VocabularyOption, VocabularyOptionSchema
from language2test_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from language2test_api.models.student_class import StudentClass, StudentClassSchema

class TestProvider(BaseProvider):
    def exist(self, text, test_id, cloze_id, cloze_question_id):
        found = False
        test = Test.query.filter_by(id=test_id).first()
        for index_cloze, cloze in enumerate(test.test_cloze):
            if cloze.id != cloze_id:
                continue
            for index_question, question in enumerate(cloze.questions):
                if question.id != cloze_question_id:
                    continue
                for index_option, option in enumerate(question.options):
                    if option.text == text:
                        found = True
                        break
                return found
        return found

    def add(self, data):
        data['id'] = self.generate_id(field=Test.id)
        test = Test(data)
        test.order = []
        for test_rc in data.get('test_rc'):
            rc = RC.query.filter_by(name=test_rc.get('name')).first()
            if rc:
                test.test_rc.append(rc)

        for test_cloze in data.get('test_cloze'):
            cloze = Cloze.query.filter_by(name=test_cloze.get('name')).first()
            if cloze:
                test.test_cloze.append(cloze)

        for test_writing in data.get('test_writing'):
            writing = Writing.query.filter_by(name=test_writing.get('name')).first()
            if writing:
                test.test_writing.append(writing)

        for test_vocabulary in data.get('test_vocabulary'):
            vocabulary = Vocabulary.query.filter_by(word=test_vocabulary.get('word')).first()
            if vocabulary:
                test.test_vocabulary.append(vocabulary)

        for test_user_field_category in data.get('test_user_field_category'):
            user_field_category = UserFieldCategory.query.filter_by(name=test_user_field_category.get('name')).first()
            if user_field_category:
                test.test_user_field_category.append(user_field_category)

        for mandatory_test_user_field_category in data.get('mandatory_test_user_field_category'):
            user_field_category = UserFieldCategory.query.filter_by(
                name=mandatory_test_user_field_category.get('name')).first()
            if user_field_category:
                test.mandatory_test_user_field_category.append(user_field_category)

        for test_student_class in data.get('test_student_class'):
            student_class = StudentClass.query.filter_by(name=test_student_class.get('name')).first()
            if student_class:
                test.test_student_class.append(student_class)

        for order in data.get('order'):
            test.order.append(order)

        db.session.add(test)

        return test

    def update(self, data, test):
        test.test_rc = []
        test.test_cloze = []
        test.test_writing = []
        test.test_vocabulary = []
        test.order = []
        test.test_user_field_category = []
        test.mandatory_test_user_field_category = []
        test.test_student_class = []
        for test_rc in data.get('test_rc'):
            rc = RC.query.filter_by(name=test_rc.get('name')).first()
            if rc:
                test.test_rc.append(rc)

        for test_cloze in data.get('test_cloze'):
            cloze = Cloze.query.filter_by(name=test_cloze.get('name')).first()
            if cloze:
                test.test_cloze.append(cloze)

        for test_writing in data.get('test_writing'):
            writing = Writing.query.filter_by(name=test_writing.get('name')).first()
            if writing:
                test.test_writing.append(writing)

        for test_vocabulary in data.get('test_vocabulary'):
            vocabulary = Vocabulary.query.filter_by(word=test_vocabulary.get('word')).first()
            if vocabulary:
                test.test_vocabulary.append(vocabulary)

        for test_user_field_category in data.get('test_user_field_category'):
            user_field_category = UserFieldCategory.query.filter_by(name=test_user_field_category.get('name')).first()
            if user_field_category:
                test.test_user_field_category.append(user_field_category)

        for mandatory_test_user_field_category in data.get('mandatory_test_user_field_category'):
            user_field_category = UserFieldCategory.query.filter_by(
                name=mandatory_test_user_field_category.get('name')).first()
            if user_field_category:
                test.mandatory_test_user_field_category.append(user_field_category)

        for test_student_class in data.get('test_student_class'):
            student_class = StudentClass.query.filter_by(name=test_student_class.get('name')).first()
            if student_class:
                test.test_student_class.append(student_class)

        for order in data.get('order'):
            test.order.append(order)

        db.session.add(test)


