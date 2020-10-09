from flask import request, send_file
from flask import json, jsonify, Response
from language2test_api.models.cloze import Cloze, ClozeSchema
from language2test_api.models.cloze_question import ClozeQuestion
from language2test_api.models.cloze_question_option import ClozeQuestionOption
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.cloze_provider import ClozeProvider
from language2test_api.models.test_session import TestSession, TestSessionSchema

import pandas as pd
from io import BytesIO
import re
from random import randint

test_schema = TestSessionSchema(many=False)
test_schema_many = TestSessionSchema(many=True)

provider = ClozeProvider()
provider.download_wordnet()

cloze_schema = ClozeSchema(many=False)
cloze_schema_many = ClozeSchema(many=True)

@language2test_bp.route("/cloze/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-cloze'])
def get_cloze_count():
    return provider.get_count(Cloze)

@language2test_bp.route("/cloze", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-cloze'])
def get_cloze():
    try:
        id = request.args.get('id')
        if id:
            properties = Cloze.query.filter_by(id=int(id)).first()
            result = cloze_schema.dump(properties)
            result = provider.get_correctly_typed_answers(result)
            return jsonify(result)

        name = request.args.get('name')
        if name:
            properties = Cloze.query.filter_by(name=name).first()
            result = cloze_schema.dump(properties)
            result = provider.get_correctly_typed_answers(result)
            return jsonify(result)

        properties = provider.query_all(Cloze)
        result = cloze_schema_many.dump(properties)
        result = provider.get_correctly_typed_answers_all_clozes(result)
        return jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/cloze", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def add_cloze():
    try:
        data = request.get_json()
        cloze = provider.add(data)
        result = cloze_schema.dump(cloze)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/cloze", methods=['PUT'])
@crossdomain(origin='*')
@authentication
@authorization(['update-cloze'])
def update_cloze():
    try:
        data = request.get_json()
        cloze = Cloze.query.filter_by(id=data.get('id')).first()
        if not cloze:
            cloze = Cloze.query.filter_by(name=data.get('name')).first()
        if cloze:
            if not cloze.immutable:
                if data.get('id') is None:
                    data['id'] = cloze.id
                provider.update(data, cloze)
                result = cloze_schema.dump(cloze)
                response = jsonify(result)
            else:
                response = Response(json.dumps(data), 403, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/cloze", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
@authorization(['delete-cloze'])
def delete_cloze():
    try:
        data = request.get_json()
        cloze = Cloze.query.filter_by(id=data.get('id')).first()
        if not cloze:
            cloze = Cloze.query.filter_by(name=data.get('name')).first()
        if cloze:
            if not cloze.unremovable:
                provider.delete(data, cloze)
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

@language2test_bp.route("/cloze/generate", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['read-cloze'])
def generate():
    try:
        data = request.get_json()
        text = data.get('text')
        if text:
            return Response(json.dumps(provider.generate_questions(text)), 200, mimetype="application/json")
        else:
            return Response({}, 400, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        return Response(json.dumps(error), 500, mimetype="application/json")

@language2test_bp.route("/cloze/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['export-cloze'])
def export_cloze():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            clozes = Cloze.query.all()
            for c in clozes:
                records.append({
                    "id": c.id,
                    "name": c.name,
                    "reading": c.text,
                    "filename": c.filename,
                    "category": c.test_category.name,
                    "type": c.type})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="{} summary".format('cloze test'),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format('cloze test')]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 16, format)
                worksheet.set_column('B:F', 25, format)
                writer.save()
            output.seek(0)
            return send_file(output,
                             attachment_filename='clozes' + '.xlsx',
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
                cloze_id = request.args.get('id')
                cloze = Cloze.query.filter_by(id=cloze_id).first()
                result = cloze_schema.dump(cloze)
                name = cloze.name
            if name is not None:
                cloze = Cloze.query.filter_by(id=cloze_id).first()
                result = cloze_schema.dump(cloze)


            cloze_infos = {
                "Id": cloze.id,
                "Name": cloze.name,
                "Category": cloze.test_category.name,
                "Time Limit": cloze.time_limit,
                "Type": cloze.type,
                "Filename": cloze.filename
            }
            cloze_question = {"Question": result["text"]}



            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame([cloze_infos]).to_excel(writer,
                                               sheet_name="{} summary".format(name+' cloze test'),
                                               index=False)
                pd.DataFrame([cloze_question], index=["Reading"]).to_excel(writer, startrow=3,
                                                                 sheet_name="{} summary".format(name+' cloze test'),
                                                                 header=False)
                cloze_questions_specific_infos = {
                    "Question id":'',
                    "Option 1":'',
                    "Option 2":'',
                    "Option 3":'',
                    "Option 4":'',
                    "Answer":'',

                }

                pd.DataFrame([cloze_questions_specific_infos]).to_excel(writer, startrow=5,
                                                                 sheet_name="{} summary".format(name+' cloze test'),
                                                                 index=False)
                for i in range(len(result['questions'])):
                    correct_option = result['questions'][i]['correct']
                    cloze_question_infos = {}

                    for j in range(len(result['questions'][i]['options'])):
                        question_options = result['questions'][i]['options'][j]
                        cloze_question_infos["options {}".format(j)] = question_options['text']
                    cloze_question_infos["Answer"] = result['questions'][i]['options'][correct_option-1]['text']

                    pd.DataFrame([cloze_question_infos], index=["{}".format(i+1)]).to_excel(writer, startrow=i+6,
                                                                                sheet_name="{} summary".format(name+' cloze test'),
                                                                                header=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format(name+' cloze test')]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 16, format)
                worksheet.set_column('B:I', 25, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename='clozes ' +name+ '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

@language2test_bp.route("/cloze/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['import-cloze'])
def upload_cloze():
    file = request.files.get("file")
    if file is not None:
        try:
            text = file.read().decode("utf8")
            words = list(map(lambda x: x.replace("*", ""), re.findall(r"([a-zA-z]?\*[a-zA-Z\-']+\*)", text)))
            idx = 1
            pattern = re.compile(r"(\*[a-zA-Z\-']+\*)")
            match = re.search(pattern, text)
            while match is not None:
                text = text[:match.start()] + "({})......".format(idx) + text[match.end():]
                match = re.search(pattern, text)
                idx += 1
            cloze_data = {
                "id": provider.generate_id(field=Cloze.id),
                "text": text,
                "time_limit": 600,
                "filename": " ",
                "type": "text",
                "test_category_id": 3
            }
            cloze_data["name"] = "Cloze-{}".format(cloze_data["id"])
            cloze = Cloze(cloze_data)
            db.session.add(cloze)
            for i, word in enumerate(words):
                correct = randint(1, 5)
                cloze_question = ClozeQuestion({
                    "id": provider.generate_id(field=ClozeQuestion.id),
                    "text": str(i + 1),
                    "cloze_id": cloze.id,
                    "correct": correct
                })
                answer, fake_answer = provider.generate_options(word)
                options = fake_answer[:correct - 1] + [answer] + fake_answer[correct - 1:]
                for op in options:
                    cloze_question_option = ClozeQuestionOption({
                        "id": provider.generate_id(field=ClozeQuestionOption.id),
                        "text": op,
                        "cloze_question_id": cloze_question.id
                    })
                    cloze_question.options.append(cloze_question_option)
                    db.session.add(cloze_question)
            db.session.commit()
            response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 500, mimetype="application/json")

    else:
        error = {"message": "file not found"}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response
