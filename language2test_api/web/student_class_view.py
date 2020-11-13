from flask import request, jsonify, url_for, Blueprint, send_file
from flask import json, jsonify, Response, blueprints
from language2test_api.models.student_class import StudentClass, StudentClassSchema
from language2test_api.models.role import Role, RoleSchema
from language2test_api.models.user import User, UserSchema
from language2test_api.models.user_field import UserField
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.student_class_provider import StudentClassProvider
from language2test_api.providers.user_provider import UserProvider
from language2test_api.web.user_keycloak import UserKeycloak
import pandas as pd
import math
from io import BytesIO

student_class_schema = StudentClassSchema(many=False)
student_class_schema_many = StudentClassSchema(many=True)
user_schema_many = UserSchema(many=True)


provider = StudentClassProvider()
user_provider = UserProvider()
keycloak = UserKeycloak()

@language2test_bp.route("/student_classes/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_student_classes_count():
    return provider.get_count(StudentClass)

@language2test_bp.route("/student_classes", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_student_class():
    id = request.args.get('id')
    if id:
        properties = StudentClass.query.filter_by(id=int(id)).first()
        result = student_class_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = StudentClass.query.filter_by(name=name)
        result = student_class_schema.dump(properties)
        return jsonify(result)

    display = request.args.get('display')
    if display:
        properties = StudentClass.query.filter(StudentClass.display == display).first()
        result = student_class_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(StudentClass)
    result = student_class_schema_many.dump(properties)
    return jsonify(result)





@language2test_bp.route("/student_classes", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_student_class():
    try:
        data = request.get_json()
        student_class = provider.add(data)
        db.session.commit()
        result = student_class_schema.dump(student_class)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/student_classes", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_student_class():
    try:
        data = request.get_json()
        student_class = StudentClass.query.filter_by(id=data.get('id')).first()
        if not student_class:
            student_class = StudentClass.query.filter_by(name=data.get('name')).first()
        if student_class:
            provider.update(data, student_class)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/student_classes", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_student_class():
    try:
        data = request.get_json()
        test = StudentClass.query.filter_by(id=data.get('id')).first()
        if not test:
            test = StudentClass.query.filter_by(name=data.get('name')).first()
        if test:
            db.session.delete(test)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/student_classes/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_student_class():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            studentClasses = StudentClass.query.all()
            for c in studentClasses:
                records.append({
                    "id": c.id,
                    "name": c.name,
                    "instructor": c.instructor.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="Student Class summary",
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets['Student Class summary']
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 25, format)
                worksheet.set_column('C:C', 20, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename='Student Class Summary' + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

    if specific_id is not None:
        try:
            name = request.args.get('name')
            if name is None:
                sc_id = request.args.get('id')
                sc = StudentClass.query.filter_by(id=sc_id).first()
                result = student_class_schema.dump(sc)
                name = sc.name
            else:
                sc = StudentClass.query.filter_by(name=name).first()
                result = student_class_schema.dump(sc)
            student_classes = result['student_student_class']
            student_class_infos = []
            for student_class in student_classes:
                if student_class['fields'] == []:
                    student_id = ''
                    first_language = ''
                    email = ''
                    phone = ''
                    address = ''
                    education = ''
                else:
                    for info in student_class['fields']:
                        if info['name'] == 'student_id':
                            student_id = info['value']
                            break
                        else:
                            student_id = ''
                    for info in student_class['fields']:
                        if info['name'] == 'first_language':
                            first_language = info['value']
                            break
                        else:
                            first_language = ''
                    for info in student_class['fields']:
                        if info['name'] == 'email':
                            email = info['value']
                            break
                        else:
                            email = ''
                    for info in student_class['fields']:
                        if info['name'] == 'phone':
                            phone = info['value']
                            break
                        else:
                            phone = ''
                    for info in student_class['fields']:
                        if info['name'] == 'address':
                            address = info['value']
                            break
                        else:
                            address = ''
                    for info in student_class['fields']:
                        if info['name'] == 'education':
                            education = info['value']
                            break
                        else:
                            education = ''
                student_class_infos.append({
                    " Class Id": result['id'],
                    "Class Name": result['name'],
                    "Instructor": result['instructor']['name'],
                    "Student Id": student_class['id'],
                    "Student Username": student_class['name'],
                    "First Name": student_class['first_name'],
                    "Last Name": student_class['last_name'],
                    "Student ID": student_id,
                    "First Language": first_language,
                    "Email": email,
                    "Phone": phone,
                    "Address": address,
                    "Education": education
                    })

            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(student_class_infos).to_excel(writer,
                                                    sheet_name="{} summary".format(name), index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format(name)]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 25, format)
                worksheet.set_column('C:C', 20, format)
                worksheet.set_column('D:D', 20, format)
                worksheet.set_column('E:E', 20, format)
                worksheet.set_column('F:G', 20, format)
                worksheet.set_column('H:H', 20, format)
                worksheet.set_column('I:I', 20, format)
                worksheet.set_column('J:J', 28, format)
                worksheet.set_column('K:M', 20, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                                attachment_filename= name + '.xlsx',
                                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

def __import_user_in_db(d):
    try:
        user = []
        if type(d["User Name"]) == str:
            user = User.query.filter_by(name=d["User Name"]).first()
            if user is not None:
                marked = {}

                for field in user.fields:
                    if field.name == "student_id" and "Student ID" in d:
                        marked["student_id"] = True
                        field.value = d["Student ID"]
                    elif field.name == "first_language" and "First Language" in d:
                        marked["first_language"] = True
                        field.value = d["First Language"]
                    elif field.name == "email" and "Email" in d:
                        marked["email"] = True
                        field.value = d["Email"]
                    elif field.name == "education" and "Education" in d:
                        marked["education"] = True
                        field.value = d["Education"]
                    elif field.name == "phone" and "Phone" in d:
                        marked["phone"] = True
                        field.value = d["Phone"]
                    elif field.name == "address" and "Address" in d:
                        marked["address"] = True
                        field.value = d["Address"]
                if not marked.get("student_id", False) and "Student ID" in d:
                    user.fields.append(UserField(
                        {"name": "student_id", "type": "text", "value": d["Student ID"], "user_id": user.id}))
                if not marked.get("first_language", False) and "First Language" in d:
                    user.fields.append(UserField(
                        {"name": "first_language", "type": "Language",
                         "value": d["First Language"], "user_id": user.id}))
                if not marked.get("email", False) and "Email" in d:
                    user.fields.append(UserField(
                        {"name": "email", "type": "text", "value": d["Email"], "user_id": user.id}))
                if not marked.get("education", False) and "Education" in d:
                    user.fields.append(UserField(
                        {"name": "education", "type": "University", "value": d["Education"], "user_id": user.id}))
                if not marked.get("phone", False) and "Phone" in d:
                    user.fields.append(UserField(
                        {"name": "phone", "type": "text", "value": d["Phone"], "user_id": user.id}))
                if not marked.get("address", False) and "Address" in d:
                    user.fields.append(UserField(
                        {"name": "address", "type": "text", "value": d["Address"], "user_id": user.id}))
                d['db_import'] = 'Updated'
            else:
                user_data = {}
                user_data["name"] = d["User Name"]
                user_data["first_name"] = d["First Name"]
                user_data["last_name"] = d["Last Name"]
                user_data["id"] = provider.generate_id(field=User.id)
                user = User(user_data)
                role = Role.query.filter_by(name="Test Taker").first()
                user.roles.append(role)
                if "Student ID" in d:
                    user.fields.append(UserField(
                        {"name": "student_id", "type": "text", "value": d["Student ID"], "user_id": user.id}))
                if "First Language" in d:
                    user.fields.append(UserField(
                        {"name": "first_language", "type": "Language",
                         "value": d["First Language"], "user_id": user.id}))
                if "Email" in d:
                    user.fields.append(UserField(
                        {"name": "email", "type": "text", "value": d["Email"], "user_id": user.id}))
                if "Education" in d:
                    user.fields.append(UserField(
                        {"name": "education", "type": "University", "value": d["Education"], "user_id": user.id}))
                if "Phone" in d:
                    user.fields.append(UserField(
                        {"name": "phone", "type": "text", "value": d["Phone"], "user_id": user.id}))
                if "Address" in d:
                    user.fields.append(UserField(
                        {"name": "address", "type": "text", "value": d["Address"], "user_id": user.id}))
                d['db_import'] = 'Imported'
            db.session.add(user)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        user = []
        d['db_import'] = 'Error: ' + str(e)
    return user

def  __import_user_in_keycloak(user_dict, token):
    # Password for keycloak import
    if ('Password' in user_dict):
        user_password = user_dict['Password']
        # Check for empty password
        # If empty password assign username as password
        if type(user_password) != str and math.isnan(user_password):
            user_password = user_dict["User Name"]
    else:
        user_password = user_dict["User Name"]
    user_dict['Password'] = user_password

    # Import user into keycloak
    token = keycloak.import_user(user_dict, token)
    return token

@language2test_bp.route("/student_classes/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
def upload_student_class():
    raw_data = request.get_data()
    data = pd.read_excel(raw_data, engine="openpyxl")
    try:
        token_kc = []
        scs = {}
        for _, row in data.iterrows():
            d = dict(row)
            if type(d['Class Name']) == str:
                exist_sc = StudentClass.query.filter_by(name=d["Class Name"]).first()
                sc = scs.get(d["Class Name"])
                if sc is None and exist_sc is None:
                    sc_data = {}
                    sc_data["name"] = d["Class Name"]
                    sc_data["display"] = "-".join(d["Class Name"].split("_"))
                    sc_data["id"] = provider.generate_id(field=StudentClass.id)
                    instructor = User.query.filter_by(name=d["Instructor Name"]).first()
                    sc = StudentClass(sc_data)
                    if "Administrator" in map(lambda e: e.name, instructor.roles) or "Instructor" in map(lambda e: e.name, instructor.roles)\
                            or "Teacher" in map(lambda e: e.name, instructor.roles):
                        sc.instructor_id = instructor.id
                        sc.instructor = instructor
                    scs[d["Class Name"]] = sc
                user = User.query.filter_by(name=d["User Name"]).first()
                if user is None:
                    user = __import_user_in_db(d)
                    if user:
                        token_kc = __import_user_in_keycloak(d, token_kc)
                else:
                    marked = {}
                    for field in user.fields:
                        if field.name == "student_id" and "Student ID" in d:
                            marked["student_id"] = True
                            field.value = d["Student ID"]
                        elif field.name == "first_language" and "First Language" in d:
                            marked["first_language"] = True
                            field.value = d["First Language"]
                        elif field.name == "email" and "Email" in d:
                            marked["email"] = True
                            field.value = d["Email"]
                        elif field.name == "education" and "Education" in d:
                            marked["education"] = True
                            field.value = d["Education"]
                        elif field.name == "phone" and "Phone" in d:
                            marked["phone"] = True
                            field.value = d["Phone"]
                        elif field.name == "address" and "Address" in d:
                            marked["address"] = True
                            field.value = d["Address"]
                    if not marked.get("student_id", False) and "Student ID" in d:
                        user.fields.append(UserField(
                            {"name": "student_id", "type": "text", "value": d["Student ID"], "user_id": user.id}))
                    if not marked.get("first_language", False) and "First Language" in d:
                        user.fields.append(UserField(
                            {"name": "first_language", "type": "Language",
                             "value": d["First Language"], "user_id": user.id}))
                    if not marked.get("email", False) and "Email" in d:
                        user.fields.append(UserField(
                            {"name": "email", "type": "text", "value": d["Email"], "user_id": user.id}))
                    if not marked.get("education", False) and "Education" in d:
                        user.fields.append(UserField(
                            {"name": "education", "type": "University", "value": d["Education"], "user_id": user.id}))
                    if not marked.get("phone", False) and "Phone" in d:
                        user.fields.append(UserField(
                            {"name": "phone", "type": "text", "value": d["Phone"], "user_id": user.id}))
                    if not marked.get("address", False) and "Address" in d:
                        user.fields.append(UserField(
                            {"name": "address", "type": "text", "value": d["Address"], "user_id": user.id}))
                if "Test Taker" in map(lambda e: e.name, user.roles) or "Administrator" in map(lambda e: e.name, user.roles):
                    if exist_sc is not None:
                        if user not in exist_sc.student_student_class:
                            exist_sc.student_student_class.append(user)
                    else:
                        if user not in scs[d["Class Name"]].student_student_class:
                            scs[d["Class Name"]].student_student_class.append(user)

            db.session.add_all(scs.values())
            db.session.commit()
        response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response


@language2test_bp.route("/instructor/student_classes", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_instructor_student_class():
    try:
        #Retrieve user
        user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(user, 'Instructor')
        if is_instructor:
            instructor_id =user.id
            if instructor_id:
                filters = {'instructor_id': int(instructor_id)}
                properties = provider.query_filter_by(StudentClass, filters)
                result = student_class_schema_many.dump(properties)
                return jsonify(result)
            else:
                error = {"message": "No Id found for the user."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
        else:
            error = {"message": "The user is not an instructor."}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/instructor/students", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_instructor_students():
    try:
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

        #Retrieve user
        user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(user, 'Instructor')
        if is_instructor:
            instructor_id =user.id
            if instructor_id:
                properties = provider.get_instructor_students(instructor_id, offset, limit, column, order)
                result = user_schema_many.dump(properties)
                return jsonify(result)
            else:
                error = {"message": "No Id found for the user."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
        else:
            error = {"message": "The user is not an instructor."}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/instructor/students/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_instructor_students_count():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(user, 'Instructor')
        if is_instructor:
            instructor_id = user.id
            if instructor_id:
                count = provider.get_instructor_students_count(instructor_id)
                response = Response(json.dumps(count), 200, mimetype="application/json")
            else:
                error = {"message": "No Id found for the user."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
        else:
            error = {"message": "The user is not an instructor."}
            response = Response(json.dumps(error), 403, mimetype="application/json")
        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/instructor/student_classes/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_instructor_student_class_count():
    try:
        #Retrieve user
        user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(user, 'Instructor')
        if is_instructor:
            instructor_id =user.id
            if instructor_id:
                count = provider.get_instructor_student_classes_count(instructor_id)
                response = Response(json.dumps(count), 200, mimetype="application/json")
            else:
                error = {"message": "No Id found for the user."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
        else:
            error = {"message": "The user is not an instructor."}
            response = Response(json.dumps(error), 403, mimetype="application/json")

        return response
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/test_taker/student_classes", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_taker_student_classes():
    try:
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

        #Retrieve user
        user = user_provider.get_authenticated_user()
        if user:
            is_test_taker = user_provider.has_role(user, 'Test Taker')
            if is_test_taker:
                test_taker_id =user.id
                if test_taker_id:
                    properties = provider.get_test_taker_student_classes(test_taker_id,offset,limit,column,order)
                    result = student_class_schema_many.dump(properties)
                    return jsonify(result)
                else:
                    error = {"message": "No Id found for the user."}
                    response = Response(json.dumps(error), 404, mimetype="application/json")
            else:
                error = {"message": "The user is not a test taker."}
                response = Response(json.dumps(error), 403, mimetype="application/json")
        else:
            error = {"message": "User not found."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/test_taker/student_classes/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_taker_student_classes_count():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_taker = user_provider.has_role(user, 'Test Taker')
        if is_test_taker:
            test_taker_id = user.id
            if test_taker_id:
                count = provider.get_test_taker_student_classes_count(test_taker_id)
                response = Response(json.dumps(count), 200, mimetype="application/json")
            else:
                error = {"message": "No Id found for the user."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
        else:
            error = {"message": "The user is not a test taker."}
            response = Response(json.dumps(error), 403, mimetype="application/json")

        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/instructor/student_classes/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
def instructor_student_class_upload():
    raw_data = request.get_data()
    data = pd.read_excel(raw_data, engine="openpyxl")
    try:
        current_user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(current_user, 'Instructor')
        if is_instructor:
            instructor_id = current_user.id
            token_kc = []
            scs = {}
            for _, row in data.iterrows():
                d = dict(row)
                if type(d['Class Name']) == str:
                    exist_sc = StudentClass.query.filter_by(name=d["Class Name"]).first()
                    sc = scs.get(d["Class Name"])
                    if sc is None and exist_sc is None:
                        sc_data = {}
                        sc_data["name"] = d["Class Name"]
                        sc_data["display"] = d["Class Name"]
                        sc_data["id"] = provider.generate_id(field=StudentClass.id)
                        if "Term" in d:
                            sc_data["term"] = d["Term"]
                        if "Level" in d:
                            sc_data["level"] = d["Level"]
                        if "Program" in d:
                            sc_data["program"] = d["Program"]
                        instructor = user_provider.get_authenticated_user()
                        sc = StudentClass(sc_data)
                        if "Administrator" in map(lambda e: e.name, instructor.roles) or "Instructor" in map(
                                lambda e: e.name, instructor.roles) \
                                or "Teacher" in map(lambda e: e.name, instructor.roles):
                            sc.instructor_id = instructor.id
                            sc.instructor = instructor
                        scs[d["Class Name"]] = sc
                    else:
                        if exist_sc.instructor_id == instructor_id:
                            user = User.query.filter_by(name=d["User Name"]).first()
                            if user is None:
                                user = __import_user_in_db(d)
                                if user:
                                    token_kc = __import_user_in_keycloak(d, token_kc)
                            else:
                                marked = {}
                                for field in user.fields:
                                    if field.name == "student_id" and "Student ID" in d:
                                        marked["student_id"] = True
                                        field.value = d["Student ID"]
                                    elif field.name == "first_language" and "First Language" in d:
                                        marked["first_language"] = True
                                        field.value = d["First Language"]
                                    elif field.name == "email" and "Email" in d:
                                        marked["email"] = True
                                        field.value = d["Email"]
                                    elif field.name == "education" and "Education" in d:
                                        marked["education"] = True
                                        field.value = d["Education"]
                                    elif field.name == "phone" and "Phone" in d:
                                        marked["phone"] = True
                                        field.value = d["Phone"]
                                    elif field.name == "address" and "Address" in d:
                                        marked["address"] = True
                                        field.value = d["Address"]
                                if not marked.get("student_id", False) and "Student ID" in d:
                                    user.fields.append(UserField(
                                        {"name": "student_id", "type": "text", "value": d["Student ID"], "user_id": user.id}))
                                if not marked.get("first_language", False) and "First Language" in d:
                                    user.fields.append(UserField(
                                        {"name": "first_language", "type": "Language",
                                         "value": d["First Language"], "user_id": user.id}))
                                if not marked.get("email", False) and "Email" in d:
                                    user.fields.append(UserField(
                                        {"name": "email", "type": "text", "value": d["Email"], "user_id": user.id}))
                                if not marked.get("education", False) and "Education" in d:
                                    user.fields.append(UserField(
                                        {"name": "education", "type": "University", "value": d["Education"],
                                         "user_id": user.id}))
                                if not marked.get("phone", False) and "Phone" in d:
                                    user.fields.append(UserField(
                                        {"name": "phone", "type": "text", "value": d["Phone"], "user_id": user.id}))
                                if not marked.get("address", False) and "Address" in d:
                                    user.fields.append(UserField(
                                        {"name": "address", "type": "text", "value": d["Address"], "user_id": user.id}))
                            if "Test Taker" in map(lambda e: e.name, user.roles) or "Administrator" in map(lambda e: e.name,
                                                                                                           user.roles):
                                if exist_sc is not None:
                                    if user not in exist_sc.student_student_class:
                                        exist_sc.student_student_class.append(user)
                                else:
                                    if user not in scs[d["Class Name"]].student_student_class:
                                        scs[d["Class Name"]].student_student_class.append(user)
                                response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
                        else:
                            error = {"message": "The class doesn't associated with the instructor"}
                            response = Response(json.dumps(error), 404, mimetype="application/json")
                db.session.add_all(scs.values())
                db.session.commit()

        else:
            error = {"message": "The user is not an instructor."}
            response = Response(json.dumps(error), 403, mimetype="application/json")

        return response
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response