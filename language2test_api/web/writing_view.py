from flask import request, send_file
from flask import json, jsonify, Response
from language2test_api.models.writing import Writing, WritingSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.writing_provider import WritingProvider
import pandas as pd
from io import BytesIO

writing_schema = WritingSchema(many=False)
writing_schema_many = WritingSchema(many=True)

provider = WritingProvider()

@language2test_bp.route("/writings/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_writings_count():
    return provider.get_count(Writing)

@language2test_bp.route("/writings", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_writing():
    id = request.args.get('id')
    if id:
        properties = Writing.query.filter_by(id=int(id)).first()
        result = writing_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = Writing.query.filter_by(name=name).first()
        result = writing_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(Writing)
    result = writing_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/writings", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_writing():
    try:
        data = request.get_json()
        writing = provider.add(data)
        result = writing_schema.dump(writing)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/writings", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_writing():
    try:
        data = request.get_json()
        writing = Writing.query.filter_by(id=data.get('id')).first()
        if not writing:
            writing = Writing.query.filter_by(name=data.get('name')).first()
        if writing:
            if not writing.immutable:
                if data.get('id') is None:
                    data['id'] = writing.id
                provider.update(data, writing)
                result = writing_schema.dump(writing)
                response = jsonify(result)
            else:
                response = Response(json.dumps(data), 403, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/writings", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_writing():
    try:
        data = request.get_json()
        writing = Writing.query.filter_by(id=data.get('id')).first()
        if not writing:
            writing = Writing.query.filter_by(name=data.get('name')).first()
        if writing:
            if not writing.unremovable:
                provider.delete(data, writing)
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

@language2test_bp.route("/writings/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_writings():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            writing_records = []
            writing_results = Writing.query.all()
            for rr in writing_results:
                writing_records.append({
                    "id": rr.id,
                    "name": rr.name,
                    "filename": rr.filename,
                    "type": rr.type,
                    "question": rr.question,
                    "word limit": rr.word_limit,
                    "time limit": rr.time_limit,
                    "category": rr.test_category.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(writing_records).to_excel(writer,
                                               sheet_name="{} summary".format("writing test"),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format("writing test")]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:H', 16, format)
                worksheet.set_column('E:E', 60, format)

                writer.save()
            output.seek(0)
            return send_file(output,
                             attachment_filename='Writing Test' + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            response = Response(json.dumps(e), 404, mimetype="application/json")
            return response

    if specific_id is not None:
        try:
            name = request.args.get('name')
            if name is None:
                rt_id = request.args.get('id')
                rt = Writing.query.filter_by(id=rt_id).first()
                name = rt.name
            else:
                rt = Writing.query.filter_by(name=name).first()
            writing_test = {
                "Id": rt.id,
                "Name": rt.name,
                "filename": rt.filename,
                "type": rt.type,
                "Question": rt.question,
                "Category": rt.test_category.name,
                "Time Limit": rt.time_limit,
                "Word Limit": rt.word_limit,
                }

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame([writing_test]).to_excel(writer,
                                               sheet_name="Writing Test {} summary".format(rt.name),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["Writing Test {} summary".format(rt.name)]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:H', 16, format)
                worksheet.set_column('E:E', 60, format)

                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename= "Writing Test "+ name + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            response = Response(json.dumps(e), 404, mimetype="application/json")
            return response

@language2test_bp.route("/writings/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
def upload_writing():
    raw_data = request.get_data()
    data = pd.read_excel(raw_data, engine="openpyxl")
    try:
        for _, row in data.iterrows():
            d = dict(row)

            wri = {"id": provider.generate_id(field=Writing.id),
                   "name": d['Test Name'],
                   "question": d['Prompt'],
                   "word_limit": d['Word Limit'],
                   "time_limit": d['Time Limit (in seconds)'],
                   "test_category_id": 4,
                   "filename": " ",
                   "type": "text",
                   }

            writing = Writing(wri)

            db.session.add(writing)
        db.session.commit()
        response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response
