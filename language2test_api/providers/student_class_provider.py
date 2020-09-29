from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.student_class import StudentClass, StudentClassSchema
from language2test_api.models.user import User, UserSchema

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

        for student_student_class in data.get('student_student_class'):
            student = User.query.filter_by(name=student_student_class.get('name')).first()
            if student:
                student_class.student_student_class.append(student)
        return student_class
