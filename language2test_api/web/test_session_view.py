from flask import request, send_file
from flask import json, jsonify, Response
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.test_session_provider import TestSessionProvider
import pandas as pd
from io import BytesIO
from language2test_api.models.test_session import TestSession, TestSessionSchema
from language2test_api.providers.test_session_export_provider import TestSessionExportProvider

test_schema = TestSessionSchema(many=False)
test_schema_many = TestSessionSchema(many=True)
provider = TestSessionProvider()
export_provider = TestSessionExportProvider()

@language2test_bp.route("/test_sessions/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-test-session'])
def get_test_sessions_count():
    return provider.get_count(TestSession)

@language2test_bp.route("/test_sessions", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-test-session'])
def get_test_session():
    id = request.args.get('id')
    if id:
        properties = TestSession.query.filter_by(id=int(id)).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = TestSession.query.filter_by(name=name).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(TestSession)
    result = test_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/test_sessions", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['create-test-session'])
def add_test_session():
    try:
        data = request.get_json()
        data['id'] = provider.generate_id(field=TestSession.id)
        test_session = provider.add(data)
        db.session.commit()
        result = test_schema.dump(test_session)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_sessions", methods=['PUT'])
@crossdomain(origin='*')
@authentication
@authorization(['update-test-session'])
def update_test_session():
    try:
        data = request.get_json()
        test_session = TestSession.query.filter_by(id=data.get('id')).first()
        if not test_session:
            test_session = TestSession.query.filter_by(name=data.get('name')).first()
        if test_session:
            if data.get('id') is None:
                data['id'] = test_session.id
            provider.update(data, test_session)
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")

    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_sessions", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
@authorization(['delete-test-session'])
def delete_test_session():
    try:
        data = request.get_json()
        test_session = TestSession.query.filter_by(id=data.get('id')).first()
        if not test_session:
            test_session = TestSession.query.filter_by(name=data.get('name')).first()
        if test_session:
            provider.delete(data, test_session)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_sessions/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['export-test-session'])
def export_test_sessions():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            sessions = TestSession.query.all()
            for s in sessions:
                records.append({
                    "Id": s.id,
                    "Name": s.name,
                    "Test_id": s.test_id,
                    "Test_name": s.test.name,
                    "Student_id": s.user_id,
                    "Student_username": s.user.name,
                    "Start Time": s.start_datetime.strftime("%A, %B %d, %Y %I %P"),
                    "End Time": s.end_datetime.strftime("%A, %B %d, %Y %I %P"),
                    "Created Time": s.created_datetime.strftime("%A, %B %d, %Y %I %P")})

            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="Test Session Summary",
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["Test Session Summary"]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 45, format)
                worksheet.set_column('C:C', 13, format)
                worksheet.set_column('D:D', 20, format)
                worksheet.set_column('E:E', 20, format)
                worksheet.set_column('F:F', 20, format)
                worksheet.set_column('G:I', 36, format)

                max_voc_test = 0
                max_rc_test = 0
                max_cloze_test = 0
                max_writing_test = 0
                for i1 in range(len(sessions)):
                    t_s = TestSession.query.filter_by(id=i1+1).first()
                    result = test_schema.dump(t_s)
                    test_results = result['test']
                    if 'test_vocabulary' in test_results:
                        voc_results = test_results["test_vocabulary"]
                        if max_voc_test < len(voc_results):
                            max_voc_test = len(voc_results)
                    if 'test_rc' in test_results:
                        rc_results = test_results["test_rc"]
                        if max_rc_test < len(rc_results):
                            max_rc_test = len(rc_results)

                    if 'test_cloze' in test_results:
                        cloze_results = test_results["test_cloze"]
                        if max_cloze_test < len(cloze_results):
                            max_cloze_test = len(cloze_results)
                    if 'test_writing' in test_results:
                        writing_results = test_results["test_writing"]
                        if max_writing_test < len(writing_results):
                            max_writing_test = len(writing_results)

                #for detailed test info
                for i2 in range(len(sessions)):
                    t_s = TestSession.query.filter_by(id=i2 + 1).first()
                    result = test_schema.dump(t_s)
                    test_results = result['test']
                    if 'test_rc' in test_results:
                        max_rc_counter = 0
                        for irc in range(len(rc_results)):
                            rc_questions = test_results["test_rc"][irc]['questions']
                            for jrc in range(len(rc_questions)):
                                max_rc_counter = max_rc_counter + 1
                        if max_rc_test < max_rc_counter:
                            max_rc_test = max_rc_counter
                    if 'test_cloze' in test_results:
                        max_cloze_counter = 0
                        for icloze in range(len(cloze_results)):
                            cloze_questions = test_results["test_cloze"][icloze]['questions']
                            for jcloze in range(len(cloze_questions)):
                                max_cloze_counter = max_cloze_counter + 1
                        if max_cloze_test < max_cloze_counter:
                            max_cloze_test = max_cloze_counter
                test_info = []
                for i in range(len(sessions)):
                    t_s = TestSession.query.filter_by(id=i+1).first()
                    result = test_schema.dump(t_s)

                    test_info.append(export_provider.test_session_grade_summary(result, max_voc_test,
                                                                                max_rc_test, max_cloze_test, max_writing_test))
                pd.DataFrame(test_info).to_excel(writer,
                                               sheet_name="Test Info",
                                               index=False)
                workbook = writer.book
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet = writer.sheets["Test Info"]
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 45, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename="Test Session Summary" + '.xlsx',
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
                t_id = request.args.get('id')
                test = TestSession.query.filter_by(id=t_id).first()
                name = test.name
                t_s = TestSession.query.filter_by(id=t_id).first()
                result = test_schema.dump(t_s)
            if name:
                new_name = name.replace(" - ", " ").replace("-", " ")
                return send_file(export_provider.write_results_into_file(result, name),attachment_filename=new_name + '.zip',
                                mimetype="application/zip",
                                as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response
