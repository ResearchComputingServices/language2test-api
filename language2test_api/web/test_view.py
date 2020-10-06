import random
import re
from flask import request, send_file
from flask import json, jsonify, Response
from language2test_api.models.test import Test, TestSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.test_provider import TestProvider
from language2test_api.providers.test_export_provider import TestExportProvider
import pandas as pd
from io import BytesIO

test_schema = TestSchema(many=False)
test_schema_many = TestSchema(many=True)

provider = TestProvider()

@language2test_bp.route("/test/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-test'])
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
@authorization(['read-test'])
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
@authorization(['read-test'])
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
@authorization(['create-test'])
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
@authorization(['update-test'])
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
@authorization(['delete-test'])
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
@authorization(['export-test'])
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
