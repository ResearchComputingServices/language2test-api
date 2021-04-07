from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test import Test, TestSchema
from language2test_api.models.rc import RC, RCSchema
from language2test_api.models.cloze import Cloze, ClozeSchema
from language2test_api.models.writing import Writing, WritingSchema
from language2test_api.models.vocabulary import Vocabulary, VocabularySchema, VocabularyOption, VocabularyOptionSchema
from language2test_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from language2test_api.providers.user_provider import UserProvider
from language2test_api.models.test_session import TestSession
from language2test_api.models.test_assignation import TestAssignation
from sqlalchemy.sql import text
from datetime import datetime

user_provider = UserProvider()


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
        user_authenticated = user_provider.get_authenticated_user()
        data['id'] = self.generate_id(field=Test.id)
        data['created_by_user_id'] = user_authenticated.id
        test = Test(data)
        test.order = []
        for test_rc in data.get('test_rc'):
            rc = RC.query.filter_by(name=test_rc.get('name')).first()
            if rc:
                rc.unremovable = True  #An RC is added to a test (it cannot be deleted)
                test.test_rc.append(rc)

        for test_cloze in data.get('test_cloze'):
            cloze = Cloze.query.filter_by(name=test_cloze.get('name')).first()
            if cloze:
                cloze.unremovable = True
                test.test_cloze.append(cloze)

        for test_writing in data.get('test_writing'):
            writing = Writing.query.filter_by(name=test_writing.get('name')).first()
            if writing:
                writing.unremovable = True
                test.test_writing.append(writing)

        for test_vocabulary in data.get('test_vocabulary'):
            vocabulary = Vocabulary.query.filter_by(word=test_vocabulary.get('word')).first()
            if vocabulary:
                vocabulary.unremovable = True
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

        for order in data.get('order'):
            test.order.append(order)

        if test.cloned_from_id is not None:
            test_clone = Test.query.filter_by(id=test.cloned_from_id).first()
            if test_clone:
                test_clone.unremovable = True

        db.session.add(test)

        return test

    def update(self, data, test):

        #Unremovable flags are set to false
        self.update_unremovable_flag(test, False)

        test.test_rc = []
        test.test_cloze = []
        test.test_writing = []
        test.test_vocabulary = []
        test.order = []
        test.test_user_field_category = []
        test.mandatory_test_user_field_category = []
        for test_rc in data.get('test_rc'):
            rc = RC.query.filter_by(name=test_rc.get('name')).first()
            if rc:
                rc.unremovable = True
                test.test_rc.append(rc)

        for test_cloze in data.get('test_cloze'):
            cloze = Cloze.query.filter_by(name=test_cloze.get('name')).first()
            if cloze:
                cloze.unremovable = True
                test.test_cloze.append(cloze)

        for test_writing in data.get('test_writing'):
            writing = Writing.query.filter_by(name=test_writing.get('name')).first()
            if writing:
                writing.unremovable = True
                test.test_writing.append(writing)

        for test_vocabulary in data.get('test_vocabulary'):
            vocabulary = Vocabulary.query.filter_by(word=test_vocabulary.get('word')).first()
            if vocabulary:
                vocabulary.unremovable = True
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

        for order in data.get('order'):
            test.order.append(order)

        db.session.add(test)


    #Updates unremovable flag
    #in test_rc, test_cloze, test_vocabulary
    def update_unremovable_flag(self, test, value):
        test_rc = test.test_rc
        for rc in test_rc:
            rc.unremovable = value

        test_cloze = test.test_cloze
        for cloze in test_cloze:
            cloze.unremovable =value

        test_vocabulary = test.test_vocabulary
        for vocabulary in test_vocabulary:
            vocabulary.unremovable = value

        test_writing = test.test_writing
        for writing in test_writing:
            writing.unremovable = value



    def query_test_with_sessions(self, limit,offset,column,order):

        p = 'test_' + column + ' ' + order
        #p = 'test_created_datetime' + ' ' + 'desc'

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            tests = db.session.query(Test).join(TestSession).filter(Test.id == TestSession.test_id).order_by(text(p)).paginate(page=page, per_page=limit, error_out=False).items
        else:
            tests = db.session.query(Test).join(TestSession).filter(Test.id == TestSession.test_id).order_by(text(p)).all()

        return tests


    def query_test_with_sessions_count(self):

        tests = db.session.query(Test).join(TestSession).filter(Test.id == TestSession.test_id).all()
        dict = {"count": len(tests)}

        return dict


    def query_upcoming_tests(self, start_datetime, limit,offset,column,order):

        p = 'test_' + column + ' ' + order
        #p = 'test_created_datetime' + ' ' + 'desc'

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1

            tests = db.session.query(Test).join(TestAssignation).filter(Test.id == TestAssignation.test_id, start_datetime<=TestAssignation.end_datetime).order_by(text(p)).paginate(page=page,per_page=limit,error_out=False).items
        else:
            tests = db.session.query(Test).join(TestAssignation).filter(Test.id == TestAssignation.test_id,
                                                                        start_datetime <= TestAssignation.end_datetime).order_by(text(p)).all()

        return tests


    def query_upcoming_tests_count(self, start_datetime):

        if not start_datetime:
            start_datetime = datetime.datetime.utcnow()

        tests = db.session.query(Test).join(TestAssignation).filter(Test.id == TestAssignation.test_id,start_datetime<=TestAssignation.end_datetime).all()

        dict = {"count": len(tests)}

        return dict

    def query_tests_not_in_use(self, limit, offset, column, order):
        p = 'test_' + column + ' ' + order

        tests_in_use = []
        # Query tests with sessions
        test_sessions = TestSession.query.all()
        for session in test_sessions:
            if session.test_id and session.test_id not in tests_in_use:
                tests_in_use.append(session.test_id)

        test_assignations = TestAssignation.query.all()
        for assignation in test_assignations:
            if assignation.test_id and assignation.test_id not in tests_in_use:
                tests_in_use.append(assignation.test_id)

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            tests_not_in_use = db.session.query(Test).filter(~Test.id.in_(tests_in_use)).order_by(text(p)).paginate(
                page=page, per_page=limit, error_out=False).items
        else:
            tests_not_in_use = db.session.query(Test).filter(~Test.id.in_(tests_in_use)).all()

        return tests_not_in_use


    def query_tests_not_in_use_count(self):

        tests_in_use = []

        # Query tests with sessions
        test_sessions =TestSession.query.all()
        for session in test_sessions:
            if session.test_id not in tests_in_use:
                tests_in_use.append(session.test_id)

        test_assignations = TestAssignation.query.all()
        for assignation in test_assignations:
            if assignation.test_id not in tests_in_use:
                tests_in_use.append(assignation.test_id)

        tests_not_in_use = db.session.query(Test).filter(~Test.id.in_(tests_in_use)).all()

        dict = {"count": len(tests_not_in_use)}

        return dict



    def query_cloned_tests(self, limit, offset, column, order):

        p = 'test_' + column + ' ' + order
        # p = 'test_created_datetime' + ' ' + 'desc'

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1

            tests = db.session.query(Test).filter(Test.cloned_from_id != None).order_by(text(p)).paginate(page=page, per_page=limit, error_out=False).items
        else:
            tests = db.session.query(Test).filter(Test.cloned_from_id != None).order_by(text(p)).all()

        return tests


    def query_cloned_tests_count(self):

        tests = db.session.query(Test).filter(Test.cloned_from_id != None).all()

        dict = {"count": len(tests)}

        return dict





