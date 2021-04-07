from language2test_api.extensions import db, ma
from language2test_api.providers.test_session_results_vocabulary_provider import TestSessionResultsVocabularyProvider
from language2test_api.providers.test_session_results_rc_provider import TestSessionResultsRCProvider
from language2test_api.providers.test_session_results_cloze_provider import TestSessionResultsClozeProvider
from language2test_api.providers.test_session_results_writing_provider import TestSessionResultsWritingProvider
from language2test_api.models.test_session import TestSession, TestSessionSchema
from language2test_api.models.test_assignation import TestAssignation
from language2test_api.models.test import Test
from language2test_api.models.student_class import StudentClass
from sqlalchemy.sql import text
from flask import request
from datetime import datetime

class TestSessionProvider(TestSessionResultsVocabularyProvider,
                          TestSessionResultsRCProvider,
                          TestSessionResultsClozeProvider,
                          TestSessionResultsWritingProvider):
    def __init__(self):
        super().__init__()

    def add(self, data):
        test_session = TestSession(data)
        test_session = self.add_results_vocabulary(data, test_session)
        test_session = self.add_results_rc(data, test_session)
        test_session = self.add_results_cloze(data, test_session)
        test_session = self.add_results_writing(data, test_session)
        if test_session.test_id is not None:
            test = Test.query.filter_by(id=test_session.test_id).first()
            if test:
                test.immutable = True
                test.unremovable = True
        db.session.add(test_session)
        return test_session

    def update(self, data, test_session):
        data = self.add_category_to_data(data)
        test_session.start_datetime = data.get('start_datetime')
        test_session.end_datetime = data.get('end_datetime')
        test_session.class_id = data.get('class_id')
        test_session.result_as_json = data.get('result_as_json')
        data_test = data.get('test')
        test_session.test_id = data_test['id']
        data_user = data.get('user')
        test_session.user_id = data_user['id']
        test_session = self.update_results_vocabulary(data, test_session)
        test_session = self.update_results_rc(data, test_session)
        test_session = self.update_results_cloze(data, test_session)
        test_session = self.update_results_writing(data, test_session)
        db.session.commit()
        return test_session

    def delete(self, data, test_session):
        test_session = self.delete_results_vocabulary(data, test_session)
        test_session = self.delete_results_rc(data, test_session)
        test_session = self.delete_results_cloze(data, test_session)
        self.delete_results_writing(data, test_session)
        if test_session.test_id is not None:
            test = Test.query.filter_by(id=test_session.test_id).first()
            if test:
                test.immutable = False
                test.unremovable = False
        db.session.query(TestSession).filter(TestSession.id == data.get('id')).delete()


    def get_test_sessions_ids(self, test_assignation_id):

        test_sessions_ids = []

        # Query test_assignation to retrieve test_id
        test_assignation = TestAssignation.query.filter_by(id=test_assignation_id).first()

        if test_assignation:
            # Get all test_sessions that include the test_id
            test_sessions_with_test_id = TestSession.query.filter_by(test_id=test_assignation.test_id).all()

            # test_sessions_per_test_id_2    Use a joint?
            # users = users.join(User.roles).filter(Role.id.in_(role.id for role in roles))

            for test_session in test_sessions_with_test_id:

                # Test session created_datetime should fall in test_assignation datetime period to take the test
                if test_session.created_datetime >= test_assignation.start_datetime and test_session.created_datetime <= test_assignation.end_datetime:

                    # Since the same test can be assigned to multiple test assignations
                    # Check if the user that created the test session is in at least one class assigned in the test assignation
                    student_classes_with_user = db.session.execute(
                        'SELECT * FROM student_student_class WHERE student_id = :val', {'val': test_session.user_id})

                    added = False
                    for item_sc in student_classes_with_user:
                        student_class_id = item_sc['student_class_id']

                        for assignation_class in test_assignation.student_class:
                            if student_class_id == assignation_class.id:
                                test_sessions_ids.append(test_session.id)
                                added = True
                                break

                        if added:
                            break

        return list(set(test_sessions_ids))


    def get_test_sessions_for_test_assignation(self, test_assignation_id):

        limit = request.args.get('limit')
        offset = request.args.get('offset')

        if 'column' in request.args:
            column = request.args.get('column')
        else:
            column = 'id'

        if 'order' in request.args:
            order = request.args.get('order')
        else:
            order = 'asc'


        test_sessions_ids = self.get_test_sessions_ids(test_assignation_id)
        p = column + ' ' + order

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            test_sessions = TestSession.query.filter(TestSession.id.in_(test_sessions_ids)).order_by(text(p)).paginate(page=page,per_page=limit,error_out=False).items
        else:
            test_sessions = TestSession.query.filter(TestSession.id.in_(test_sessions_ids)).order_by(text(p)).all()

        return test_sessions



    def get_test_sessions_for_test_assignation_count(self, test_assignation_id):

        test_sessions_ids = self.get_test_sessions_ids(test_assignation_id)
        dict = {"count": len(test_sessions_ids)}

        return dict


    def get_test_sessions_for_test(self, test_id, limit,offset,column,order):

        p = column + ' ' + order

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            test_sessions = db.session.query(TestSession).filter(TestSession.test_id == test_id).order_by(text(p)).paginate(page=page, per_page=limit, error_out=False).items
        else:
            test_sessions = db.session.query(TestSession).filter(TestSession.test_id == test_id).order_by(text(p)).all()

        return test_sessions


    def get_test_sessions_for_test_count(self, test_id):

        tests = db.session.query(TestSession).filter(TestSession.test_id == test_id).all()
        dict = {"count": len(tests)}

        return dict


    def filter_test_sessions_count(self, column, order, limit=None, offset=None, start_datetime_rq=None, end_datetime_rq=None, class_id=None, student_id=None, test_id=None, instructor_id=None):
        test_sessions = self.filter_test_sessions(column, order, limit, offset, start_datetime_rq, end_datetime_rq, class_id, student_id, test_id, instructor_id)
        dict = {"count": len(test_sessions)}

        return dict


    def filter_test_sessions(self, column, order, limit=None, offset=None, start_datetime_rq=None, end_datetime_rq=None, class_id=None, student_id=None, test_id=None, instructor_id=None):

        filters_list = []

        if start_datetime_rq:
            start_datetime = datetime.strptime(start_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')
            filters_list.append(TestSession.created_datetime >= start_datetime)

        if end_datetime_rq:
            end_datetime = datetime.strptime(end_datetime_rq, '%Y-%m-%dT%H:%M:%S.%fZ')
            filters_list.append(TestSession.created_datetime <=end_datetime)

        if class_id:
            filters_list.append(TestSession.class_id==class_id)

        if student_id:
            filters_list.append(TestSession.user_id == student_id)

        if test_id:
            filters_list.append(TestSession.test_id == test_id)

        filters = tuple(filters_list)
        query = db.session.query(TestSession).filter(*filters)

        if instructor_id:
            query = query.join(StudentClass).filter(TestSession.class_id==StudentClass.id, StudentClass.instructor_id==instructor_id)

        p = 'test_session_' + column + ' ' + order
        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            test_sessions = query.order_by(text(p)).paginate(page=page,per_page=limit,error_out=False).items
        else:
            test_sessions =query.order_by(text(p)).all()

        return test_sessions





