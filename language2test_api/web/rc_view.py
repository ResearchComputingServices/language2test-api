from flask import request, send_file
from flask import json, jsonify, Response
from language2test_api.models.rc import RC, RCSchema
from language2test_api.models.rc_question import RCQuestion
from language2test_api.models.rc_question_option import RCQuestionOption
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.rc_provider import RCProvider
from language2test_api.models.test_session import TestSession, TestSessionSchema
import pandas as pd
from io import BytesIO
import re
rc_schema = RCSchema(many=False)
rc_schema_many = RCSchema(many=True)

provider = RCProvider()

test_schema = TestSessionSchema(many=False)
test_schema_many = TestSessionSchema(many=True)

@language2test_bp.route("/rc/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_rc_count():
    return provider.get_count(RC)

@language2test_bp.route("/rc", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_rc():
    id = request.args.get('id')
    if id:
        properties = RC.query.filter_by(id=int(id)).first()
        result = rc_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = RC.query.filter_by(name=name).first()
        result = rc_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(RC)
    result = rc_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/rc", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_rc():
    try:
        data = request.get_json()
        rc = provider.add(data)
        db.session.commit()
        result = rc_schema.dump(rc)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/rc", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_rc():
    try:
        data = request.get_json()
        rc = RC.query.filter_by(id=data.get('id')).first()
        if not rc:
            rc = RC.query.filter_by(name=data.get('name')).first()
        if rc:
            if not rc.immutable:
                if data.get('id') is None:
                    data['id'] = rc.id
                provider.update(data, rc)
                result = rc_schema.dump(rc)
                response = jsonify(result)
            else:
                response = Response(json.dumps(data), 403, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/rc", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_rc():
    try:
        data = request.get_json()
        rc = RC.query.filter_by(id=data.get('id')).first()
        if not rc:
            rc = RC.query.filter_by(name=data.get('name')).first()
        if rc:
            if not rc.unremovable:
                provider.delete(data, rc)
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

@language2test_bp.route("/rc/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_rc():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            rcs = RC.query.all()
            for rc in rcs:
                records.append({
                    "id": rc.id,
                    "name": rc.name,
                    "reading": rc.text,
                    "filename": rc.filename,
                    "Time Limit": rc.time_limit,
                    "category": rc.test_category.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="{} summary".format("rc test"),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format("rc test")]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 16, format)
                worksheet.set_column('B:B', 16, format)
                worksheet.set_column('C:C', 45, format)
                worksheet.set_column('D:D', 25, format)
                worksheet.set_column('E:E', 16, format)
                worksheet.set_column('F:F', 16, format)
                writer.save()
            output.seek(0)
            return send_file(output,
                             attachment_filename='Reading Comprehension' + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            response = Response(json.dumps(e), 404, mimetype="application/json")
            return response

    if specific_id is not None:
        try:
            name = request.args.get('name')
            if name is None:
                rc_id = request.args.get('id')
                rc = RC.query.filter_by(id=rc_id).first()
                rc_result = rc_schema.dump(rc)
                name = rc.name
            else:
                rc = RC.query.filter_by(name=name).first()
                rc_result = rc_schema.dump(rc)
            rc_infos = {
                "Id": rc.id,
                "Name": rc.name,
                "Category": rc.test_category.name,
                "Time Limit": rc.time_limit,
                "Type": rc.type
            }
            rc_reading_info = {"Reading": rc_result['text']}
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame([rc_infos]).to_excel(writer,
                                               sheet_name="{} summary".format("rc test"),
                                               index=False)

                pd.DataFrame([rc_reading_info], index=["Reading"]).to_excel(writer, startrow=3,
                                                                 sheet_name="{} summary".format("rc test"),
                                                                 header=False)
                rc_questions_specific_infos = {
                    "Question id":'',
                    "Question":'',
                    "Option 1":'',
                    "Option 2":'',
                    "Option 3":'',
                    "Option 4":'',
                    "Answer":'',

                }
                pd.DataFrame([rc_questions_specific_infos]).to_excel(writer, startrow=5,
                                                                 sheet_name="{} summary".format("rc test"),
                                                                 index=False)
                for i in range(len(rc_result['questions'])):
                    correct_option = rc_result['questions'][i]['correct']
                    rc_question_infos = {
                        "Question": rc_result['questions'][i]['text'],
                    }

                    for j in range(len(rc_result['questions'][i]['options'])):
                        question_options = rc_result['questions'][i]['options'][j]
                        rc_question_infos["options {}".format(j)] = question_options['text']
                    rc_question_infos["Answer"] = rc_result['questions'][i]['options'][correct_option-1]['text']

                    pd.DataFrame([rc_question_infos], index=["{}".format(i+1)]).to_excel(writer, startrow=i+6,
                                                                                sheet_name="{} summary".format("rc test"),
                                                                                header=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format("rc test")]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 16, format)
                worksheet.set_column('B:B', 55, format)
                worksheet.set_column('C:C', 45, format)
                worksheet.set_column('D:D', 45, format)
                worksheet.set_column('E:E', 45, format)
                worksheet.set_column('F:F', 45, format)
                worksheet.set_column('G:G', 45, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename='Reading Comprehension ' +name+ '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            response = Response(json.dumps(e), 404, mimetype="application/json")
            return response



@language2test_bp.route("/rc/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
def upload_rc():
    file = request.files.get("file")
    if file is not None:
        try:
            text = file.read().decode("utf8")
            reading = re.findall(r"<reading>(.*?)</reading>", text, re.DOTALL)[0].strip()
            questions = list(map(lambda x: provider.gen_question(x),
                                 re.findall(r"<question>(.*?)</question>", text, re.DOTALL)))
            rc_data = {
                "id": provider.generate_id(field=RC.id),
                "text": reading,
                "time_limit": 600,
                "test_category_id": 2
            }
            rc_data["name"] = "RC-{}".format(rc_data["id"])
            rc = RC(rc_data)
            db.session.add(rc)
            for question in questions:
                rc_question = RCQuestion({
                    "id": provider.generate_id(field=RCQuestion.id),
                    "text": question["question"],
                    "rc_id": rc.id,
                    "correct": question["correct"]
                })
                rc_question.rc = rc
                for op in question["options"]:
                    rc_question_option = RCQuestionOption({
                        "id": provider.generate_id(field=RCQuestionOption.id),
                        "text": op,
                        "rc_question_id": rc_question.id
                    })
                    rc_question.options.append(rc_question_option)
                    db.session.add(rc_question)

            db.session.commit()
            response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 500, mimetype="application/json")

    else:
        error = {"message": "file not found"}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response
