import random
import re
from flask import request, send_file
from flask import json, jsonify, Response

from language2test_api.models import TestAssignation
from language2test_api.models.test import Test, TestSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.test_provider import TestProvider
from language2test_api.providers.test_export_provider import TestExportProvider
from language2test_api.providers.user_provider import UserProvider
from language2test_api.models.test_session import TestSession
import pandas as pd
import datetime
from io import BytesIO


test_schema = TestSchema(many=False)
test_schema_many = TestSchema(many=True)

provider = TestProvider()
user_provider = UserProvider()

@language2test_bp.route("/test/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_count():
    return provider.get_count(Test)


def __remove_correct_and_shuffle_options(tests):
    test_types = ['test_rc', 'test_cloze', 'test_vocabulary']

    for test in tests:
        for type in test_types:
            if type in test:
                for test_type in test[type]:
                    if 'questions' in test_type: #Shuffle questions in each test
                        for question in test_type['questions']:
                            question['correct'] = 0
                            random.shuffle(question['options'])
                    else:
                        if 'correct' in test_type:  # Vocabulary test is one word with several options.
                            test_type['correct'] = 0
                            random.shuffle(test_type['options'])

    #Remove questions-word from cloze
    for test in tests:
        if test['test_cloze']:
            cloze_tests = test['test_cloze']
            for cloze in cloze_tests:
                pattern = re.compile(r"(\*.*?\*)")
                cloze_text = re.sub(pattern, '**', cloze['text'])
                cloze['text'] = cloze_text
                print(cloze_text)

    return tests

def __shuffle_test_order(tests):
    test_types = ['test_rc', 'test_cloze', 'test_vocabulary']

    for test in tests:
        for type in test_types:
            if type in test:
                random.shuffle(test[type])

    return tests


@language2test_bp.route("/test/wizard", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_wizard():
    id = request.args.get('id')
    if id:
        properties = Test.query.filter_by(id=int(id)).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = Test.query.filter_by(name=name).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(Test)
    result = test_schema_many.dump(properties)
    result = __remove_correct_and_shuffle_options(result)
    result = __shuffle_test_order(result)
    return jsonify(result)

    return tests

@language2test_bp.route("/test", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test():
    id = request.args.get('id')
    if id:
        properties = Test.query.filter_by(id=int(id)).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = Test.query.filter_by(name=name).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(Test)
    result = test_schema_many.dump(properties)
    return jsonify(result)


@language2test_bp.route("/test", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_test():
    try:
        data = request.get_json()
        test = provider.add(data)
        db.session.commit()
        result = test_schema.dump(test)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_test():
    try:
        data = request.get_json()
        test = Test.query.filter_by(id=data.get('id')).first()
        if not test:
            test = Test.query.filter_by(name=data.get('name')).first()
        if test:
            if not test.immutable:
                if data.get('id') is None:
                    data['id'] = test.id
                provider.update(data, test)
                db.session.commit()
                result = test_schema.dump(test)
                response = jsonify(result)
            else:
                response = Response(json.dumps(data), 403, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_test():
    try:
        data = request.get_json()
        test = Test.query.filter_by(id=data.get('id')).first()
        if not test:
            test = Test.query.filter_by(name=data.get('name')).first()
        if test:
            if not test.immutable:
                provider.update_unremovable_flag(test, False)
                db.session.delete(test)
                db.session.commit()
                response = Response(json.dumps(data), 200, mimetype="application/json")
            else:
                response = Response(json.dumps(data), 403, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_test():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            tests = Test.query.all()
            for test in tests:
                records.append({
                    "id": test.id,
                    "name": test.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="{} summary".format("test"),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format("test")]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 16, format)
                worksheet.set_column('B:B', 18, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename="Test" + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response
    if specific_id is not None:
        try:
            name = request.args.get('name')
            test_id = request.args.get('id')
            if name is None:
                tests = Test.query.filter_by(id=test_id).first()
                name = tests.name
            if name is not None:
                return send_file(TestExportProvider.write_results_into_file(test_id),
                                 attachment_filename=name+ ' test information' + '.xlsx',
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 as_attachment=True, cache_timeout=-1)

        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response



@language2test_bp.route("/test_developer/test_with_sessions", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_tests_with_sessions():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
            limit = request.args.get('limit')
            offset = request.args.get('offset')

            if 'column' in request.args:
                column = request.args.get('column')
            else:
                column = 'created_datetime'

            if 'order' in request.args:
                order = request.args.get('order')
            else:
                order = 'desc'

            properties = provider.query_test_with_sessions(limit,offset,column,order)
            result = test_schema_many.dump(properties)
            return jsonify(result)
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")

    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")

    return response


@language2test_bp.route("/test_developer/test_with_sessions/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_tests_with_sessions_count():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
            count = provider.query_test_with_sessions_count()
            response = Response(json.dumps(count), 200, mimetype="application/json")
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/test_developer/upcoming_tests", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_upcoming_tests():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
            start_datetime = request.args.get('start_datetime')
            if not start_datetime:
                start_datetime = datetime.datetime.utcnow()

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

            properties = provider.query_upcoming_tests(start_datetime,limit,offset,column,order)
            result = test_schema_many.dump(properties)
            return jsonify(result)
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")

    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")

    return response




@language2test_bp.route("/test_developer/upcoming_tests/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_upcoming_tests_with_count():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
            start_datetime = request.args.get('start_datetime')
            if not start_datetime:
                start_datetime = datetime.datetime.utcnow()
            
            count = provider.query_upcoming_tests_count(start_datetime)
            response = Response(json.dumps(count), 200, mimetype="application/json")
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response






@language2test_bp.route("/test_developer/test_not_in_use/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_tests_not_in_use_count():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
            count = provider.query_tests_not_in_use_count()
            response = Response(json.dumps(count), 200, mimetype="application/json")
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/test_developer/test_not_in_use", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_tests_not_in_use():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:

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

            properties = provider.query_tests_not_in_use(limit,offset,column,order)
            result = test_schema_many.dump(properties)
            return jsonify(result)
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")

    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")

    return response


@language2test_bp.route("/test_developer/cloned_tests", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_cloned_tests():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
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

            properties = provider.query_cloned_tests(limit,offset,column,order)
            result = test_schema_many.dump(properties)
            return jsonify(result)
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")

    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")

    return response

@language2test_bp.route("/test_developer/cloned_tests/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_cloned_tests_count():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_test_developer = user_provider.has_role(user, 'Test Developer')

        if is_test_developer:
            count = provider.query_cloned_tests_count()
            response = Response(json.dumps(count), 200, mimetype="application/json")
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_developer/test/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def test_developer_export_test():
    user = user_provider.get_authenticated_user()
    is_test_developer = user_provider.has_role(user, 'Test Developer')
    if is_test_developer:
        specific_id = request.args.get('id')
        if specific_id is None:
            try:
                records = []
                tests = Test.query.all()
                for test in tests:
                    records.append({
                        "id": test.id,
                        "name": test.name})

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    pd.DataFrame(records).to_excel(writer,
                                                   sheet_name="{} summary".format("test"),
                                                   index=False)
                    workbook = writer.book
                    worksheet = writer.sheets["{} summary".format("test")]
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 16, format)
                    worksheet.set_column('B:B', 18, format)
                    writer.save()

                output.seek(0)
                return send_file(output,
                                 attachment_filename="Test" + '.xlsx',
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 as_attachment=True, cache_timeout=-1)
            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response
        if specific_id is not None:
            try:
                name = request.args.get('name')
                test_id = request.args.get('id')
                if name is None:
                    tests = Test.query.filter_by(id=test_id).first()
                    name = tests.name
                if name is not None:
                    return send_file(TestExportProvider.write_results_into_file(test_id),
                                     attachment_filename=name+ ' test information' + '.xlsx',
                                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     as_attachment=True, cache_timeout=-1)

            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response

    else:
        error = {"message": "Access Denied"}
        response = Response(json.dumps(error), 403, mimetype="application/json")

    return response


@language2test_bp.route("/test_developer/upcoming_tests/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def upcoming_tests_developer_export_test():
    user = user_provider.get_authenticated_user()
    is_test_developer = user_provider.has_role(user, 'Test Developer')
    if is_test_developer:
        specific_id = request.args.get('id')
        start_datetime = datetime.datetime.utcnow()
        if specific_id is None:
            try:
                records = []
                tests = db.session.query(Test).join(TestAssignation).filter(Test.id == TestAssignation.test_id,
                                                                        start_datetime <= TestAssignation.end_datetime).all()


                for test in tests:
                    records.append({
                        "id": test.id,
                        "name": test.name})

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    pd.DataFrame(records).to_excel(writer,
                                                   sheet_name="{} summary".format("test"),
                                                   index=False)
                    workbook = writer.book
                    worksheet = writer.sheets["{} summary".format("test")]
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 16, format)
                    worksheet.set_column('B:B', 18, format)
                    writer.save()

                output.seek(0)
                return send_file(output,
                                 attachment_filename="Test" + '.xlsx',
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 as_attachment=True, cache_timeout=-1)
            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response
        if specific_id is not None:
            try:
                tests = db.session.query(Test).join(TestAssignation).filter(Test.id == TestAssignation.test_id,
                                                                            start_datetime <= TestAssignation.end_datetime).all()
                for test in tests:
                    if test.id == int(specific_id):
                        name = test.name
                        return send_file(TestExportProvider.write_results_into_file(test.id),
                                             attachment_filename=name+ ' test information' + '.xlsx',
                                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             as_attachment=True, cache_timeout=-1)

            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response

    else:
        error = {"message": "Access Denied"}
        response = Response(json.dumps(error), 403, mimetype="application/json")

    return response


@language2test_bp.route("/test_developer/test_with_sessions/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def test_with_sessions_developer_export_test():
    user = user_provider.get_authenticated_user()
    is_test_developer = user_provider.has_role(user, 'Test Developer')
    if is_test_developer:
        specific_id = request.args.get('id')
        if specific_id is None:
            try:
                records = []
                tests = db.session.query(Test).join(TestSession).filter(Test.id == TestSession.test_id).all()
                for test in tests:
                    records.append({
                        "id": test.id,
                        "name": test.name})

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    pd.DataFrame(records).to_excel(writer,
                                                   sheet_name="{} summary".format("test"),
                                                   index=False)
                    workbook = writer.book
                    worksheet = writer.sheets["{} summary".format("test")]
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 16, format)
                    worksheet.set_column('B:B', 18, format)
                    writer.save()

                output.seek(0)
                return send_file(output,
                                 attachment_filename="Test" + '.xlsx',
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 as_attachment=True, cache_timeout=-1)
            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response
        if specific_id is not None:
            try:
                tests = db.session.query(Test).join(TestSession).filter(Test.id == TestSession.test_id).all()
                for test in tests:
                    if test.id == int(specific_id):
                        name = test.name
                        return send_file(TestExportProvider.write_results_into_file(test.id),
                                             attachment_filename=name+ ' test information' + '.xlsx',
                                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             as_attachment=True, cache_timeout=-1)

            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response

    else:
        error = {"message": "Access Denied"}
        response = Response(json.dumps(error), 403, mimetype="application/json")

    return response

@language2test_bp.route("/test_developer/test_not_in_use/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def test_not_in_use_developer_export_test():
    user = user_provider.get_authenticated_user()
    is_test_developer = user_provider.has_role(user, 'Test Developer')
    if is_test_developer:
        specific_id = request.args.get('id')
        tests_in_use = []
        test_sessions = TestSession.query.all()
        for session in test_sessions:
            if session.test_id not in tests_in_use:
                tests_in_use.append(session.test_id)
        test_assignations = TestAssignation.query.all()
        for assignation in test_assignations:
            if assignation.test_id not in tests_in_use:
                tests_in_use.append(assignation.test_id)
        if specific_id is None:
            try:
                records = []
                tests = db.session.query(Test).filter(~Test.id.in_(tests_in_use)).all()
                for test in tests:
                    records.append({
                        "id": test.id,
                        "name": test.name})

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    pd.DataFrame(records).to_excel(writer,
                                                   sheet_name="{} summary".format("test"),
                                                   index=False)
                    workbook = writer.book
                    worksheet = writer.sheets["{} summary".format("test")]
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 16, format)
                    worksheet.set_column('B:B', 18, format)
                    writer.save()

                output.seek(0)
                return send_file(output,
                                 attachment_filename="Test" + '.xlsx',
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 as_attachment=True, cache_timeout=-1)
            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response
        if specific_id is not None:
            try:
                tests = db.session.query(Test).filter(~Test.id.in_(tests_in_use)).all()
                for test in tests:
                    if test.id == int(specific_id):
                        name = test.name
                        return send_file(TestExportProvider.write_results_into_file(test.id),
                                             attachment_filename=name+ ' test information' + '.xlsx',
                                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             as_attachment=True, cache_timeout=-1)

            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response

    else:
        error = {"message": "Access Denied"}
        response = Response(json.dumps(error), 403, mimetype="application/json")

    return response

@language2test_bp.route("/test_developer/cloned_tests/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def cloned_tests_developer_export_test():
    user = user_provider.get_authenticated_user()
    is_test_developer = user_provider.has_role(user, 'Test Developer')
    if is_test_developer:
        specific_id = request.args.get('id')
        if specific_id is None:
            try:
                records = []
                tests = db.session.query(Test).filter(Test.cloned_from_id != None).all()
                for test in tests:
                    records.append({
                        "id": test.id,
                        "name": test.name})

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    pd.DataFrame(records).to_excel(writer,
                                                   sheet_name="{} summary".format("test"),
                                                   index=False)
                    workbook = writer.book
                    worksheet = writer.sheets["{} summary".format("test")]
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 16, format)
                    worksheet.set_column('B:B', 18, format)
                    writer.save()

                output.seek(0)
                return send_file(output,
                                 attachment_filename="Test" + '.xlsx',
                                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 as_attachment=True, cache_timeout=-1)
            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response
        if specific_id is not None:
            try:
                tests = db.session.query(Test).filter(Test.cloned_from_id != None).all()
                for test in tests:
                    if test.id == int(specific_id):
                        name = test.name
                        return send_file(TestExportProvider.write_results_into_file(test.id),
                                             attachment_filename=name+ ' test information' + '.xlsx',
                                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             as_attachment=True, cache_timeout=-1)

            except Exception as e:
                error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
                return response

    else:
        error = {"message": "Access Denied"}
        response = Response(json.dumps(error), 403, mimetype="application/json")

    return response
