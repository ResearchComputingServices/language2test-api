from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.student_class import StudentClass, StudentClassSchema
from language2test_api.models.user import User, UserSchema
from sqlalchemy.sql import text

class StudentClassProvider(BaseProvider):


    def add(self, data):
        data['id'] = self.generate_id(field=StudentClass.id)
        data_instructor = data.get('instructor')
        data = self.fill_out_name_based_on_display(data)
        if data_instructor:
            instructor_name = data_instructor.get('name')
            instructor = User.query.filter_by(name=instructor_name).first()
            if instructor:
                data['instructor_id'] = instructor.id
        student_class = StudentClass(data)

        for student_student_class in data.get('student_student_class'):
            student = User.query.filter_by(name=student_student_class.get('name')).first()
            if student:
                student_class.student_student_class.append(student)

        db.session.add(student_class)
        return student_class




    def update(self, data, student_class):
        student_class.student_student_class = []
        data_instructor = data.get('instructor')
        if data_instructor:
            instructor_name = data_instructor.get('name')
            instructor = User.query.filter_by(name=instructor_name).first()
            if instructor:
                data['instructor_id'] = instructor.id

        student_class.display = data.get('display')
        student_class.instructor_id = data.get('instructor_id')

        if 'term' in data:
            student_class.term = data.get('term')

        if 'level' in data:
            student_class.level = data.get('level')

        if 'program' in data:
            student_class.program = data.get('program')

        for student_student_class in data.get('student_student_class'):
            student = User.query.filter_by(name=student_student_class.get('name')).first()
            if student:
                student_class.student_student_class.append(student)
        return student_class



    def __get_instructor_students_ids(self, instructor_id):
        # 1. Get all instructor classes
        instructor_classes = StudentClass.query.filter_by(instructor_id=instructor_id).all()

        # 2.Retrieve all students
        all_students_ids = []

        for _class in instructor_classes:
            for _student in _class.student_student_class:
                all_students_ids.append(_student.id)

        # 3. Remove repeated/duplicated ids
        all_students_ids = list(set(all_students_ids))

        return all_students_ids




    def get_instructor_students(self, instructor_id, offset, limit, column, order):

        all_students_ids = self.__get_instructor_students_ids(instructor_id)

        p = column + ' ' + order

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            #4. Filter query to match only the uers ids
            students = User.query.filter(User.id.in_(all_students_ids)).order_by(text(p)).paginate(page=page, per_page=limit, error_out=False).items
        else:
            students = User.query.filter(User.id.in_(all_students_ids)).order_by(text(p)).all()

        return students




    def get_instructor_students_count(self, instructor_id):

        all_students_ids = self.__get_instructor_students_ids(instructor_id)
        dict = {"count": len(all_students_ids)}

        return dict




    def get_instructor_student_classes_count(self, instructor_id):

        instructor_classes = StudentClass.query.filter_by(instructor_id=instructor_id).all()
        dict = {"count": len(instructor_classes)}

        return dict



    def __get_test_taker_sudent_classes_ids(self, test_taker_id):

        student_classes_ids = []

        # Retrieve all student classes of the user_id
        proxy_student_classes = db.session.execute('SELECT * FROM student_student_class WHERE student_id = :val',
                                                  {'val': test_taker_id})


        for item_sc in proxy_student_classes:
            student_classes_ids.append(item_sc['student_class_id'])


        return student_classes_ids






    def get_test_taker_student_classes(self, test_taker_id,  offset, limit, column, order):

        student_classes_ids = self.__get_test_taker_sudent_classes_ids(test_taker_id)

        p = column + ' ' + order

        if limit and offset:
            limit = int(limit)
            offset = int(offset)
            page = int(offset / limit) + 1
            # 4. Filter query to match only the uers ids
            student_classes= StudentClass.query.filter(StudentClass.id.in_(student_classes_ids)).order_by(text(p)).paginate(page=page,
                                                                                                   per_page=limit,
                                                                                                   error_out=False).items
        else:
            student_classes = StudentClass.query.filter(StudentClass.id.in_(student_classes_ids)).order_by(text(p)).all()

        return student_classes





    def get_test_taker_student_classes_count(self, test_taker_id):

        student_classes_ids = self.__get_test_taker_sudent_classes_ids(test_taker_id)

        dict = {"count": len(student_classes_ids)}

        return dict






