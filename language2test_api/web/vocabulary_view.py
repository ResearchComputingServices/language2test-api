from flask import request, jsonify, url_for, Blueprint, send_file
from flask import json, jsonify, Response, blueprints
from language2test_api.models.vocabulary import Vocabulary, VocabularySchema
from language2test_api.models.vocabulary_option import VocabularyOption, VocabularyOptionSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.vocabulary_provider import VocabularyProvider
from language2test_api.models.test_category import TestCategory, TestCategorySchema

from language2test_api.models.test_session import TestSession, TestSessionSchema

import pandas as pd
from io import BytesIO
import random
import numpy

test_schema = TestSessionSchema(many=False)
test_schema_many = TestSessionSchema(many=True)

vocabulary_schema = VocabularySchema(many=False)
vocabulary_schema_many = VocabularySchema(many=True)

provider = VocabularyProvider()

@language2test_bp.route("/vocabulary/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-vocabulary'])
def get_vocabulary_count():
    return provider.get_count(Vocabulary)

@language2test_bp.route("/vocabulary", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-vocabulary'])
def get_vocabulary():
    id = request.args.get('id')
    if id:
        properties = Vocabulary.query.filter_by(id=int(id)).first()
        result = vocabulary_schema.dump(properties)
        return jsonify(result)

    word = request.args.get('word')
    if word:
        properties = Vocabulary.query.filter_by(word=word).first()
        result = vocabulary_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(Vocabulary)
    result = vocabulary_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/vocabulary", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['create-vocabulary'])
def add_vocabulary():
    try:
        data = request.get_json()
        vocabulary = provider.add(data)
        result = vocabulary_schema.dump(vocabulary)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/vocabulary", methods=['PUT'])
@crossdomain(origin='*')
@authentication
@authorization(['update-vocabulary'])
def update_vocabulary():
    try:
        data = request.get_json()
        vocabulary = Vocabulary.query.filter_by(id=data.get('id')).first()
        if not vocabulary:
            vocabulary = Vocabulary.query.filter_by(word=data.get('word')).first()
        if vocabulary and not vocabulary.immutable:
            if data.get('id') is None:
                data['id'] = vocabulary.id
            provider.update(data, vocabulary)
            result = vocabulary_schema.dump(vocabulary)
            response = jsonify(result)
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/vocabulary", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
@authorization(['delete-vocabulary'])
def delete_vocabulary():
    try:
        data = request.get_json()
        vocabulary = Vocabulary.query.filter_by(id=data.get('id')).first()
        if not vocabulary:
            vocabulary = Vocabulary.query.filter_by(word=data.get('word')).first()
        if vocabulary and not vocabulary.unremovable:
            provider.delete(data, vocabulary)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/vocabulary/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['export-vocabulary'])
def export_vocabulary():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            vocabularies = Vocabulary.query.all()
            for voc in vocabularies:
                records.append({
                    "Id": voc.id,
                    "Word": voc.word,
                    "Type": voc.type,
                    "Options": ", ".join(map(lambda e: e.text, voc.options)),
                    "Correct": voc.correct,
                    "Difficulty": voc.difficulty,
                    "Time Limit": voc.time_limit,
                    "category": voc.test_category.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="{} summary".format("Vocabulary"),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format("Vocabulary")]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 20, format)
                worksheet.set_column('C:C', 20, format)
                worksheet.set_column('D:D', 55, format)
                worksheet.set_column('E:E', 13, format)
                worksheet.set_column('F:F', 13, format)
                worksheet.set_column('G:G', 13, format)
                worksheet.set_column('H:H', 20, format)
                writer.save()
            output.seek(0)
            return send_file(output,
                             attachment_filename="Vocabulary" + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

    if specific_id is not None:
        try:
            voc_id = int(request.args.get('id'))
            voc = Vocabulary.query.filter_by(id=voc_id).first()
            voc_result = vocabulary_schema.dump(voc)
            option_list = []
            for i in range(len(voc_result["options"])):
                option_list.append(voc_result["options"][i]['text'])
            name = voc.word
            voc_test = {
                "Id": voc.id,
                "Word": voc.word,
                "Type": voc.type,
                "Category": voc_result["test_category"]["name"],
                "Time Limit": voc.time_limit,
                "Options": ', '.join(option_list),
                "Correct option number": voc.correct
            }

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame([voc_test]).to_excel(writer,
                                                    sheet_name="{} details".format(name), index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} details".format(name)]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 16, format)
                worksheet.set_column('C:C', 16, format)
                worksheet.set_column('D:D', 16, format)
                worksheet.set_column('E:E', 18, format)
                worksheet.set_column('F:F', 30, format)
                worksheet.set_column('G:G', 22, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename="Vocabulary " +name+ ' details'+'.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response


@language2test_bp.route("/vocabulary/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['import-vocabulary'])
def upload_vocabulary():
    raw_data = request.get_data()
    data = pd.read_excel(raw_data, engine="openpyxl")
    try:
        for _, row in data.iterrows():
            d = dict(row)
            if d["4 Distractor"] != "nan":
                ops = [d["2 Distractor"], d["Answer"], d["3 Distractor"], d["4 Distractor"]]
            else:
                ops = [d["2 Distractor"], d["Answer"], d["3 Distractor"]]
            random.shuffle(ops)
            correct_option = ops.index(d["Answer"])
            correct_option = correct_option + 1
            dif = d["vocab_Difficulty"]
            if numpy.isnan(dif):
                dif = numpy.nan_to_num(dif)

            voc = {"word": d["stem"],
                   "type": "synonym",
                   "difficulty": int(dif),
                   "correct": int(correct_option),
                   "time_limit": "20",
                   }
            voc["id"] = provider.generate_id(field=Vocabulary.id)

            test_category = TestCategory.query.filter_by(name="Default").first()
            voc["test_category_id"] = test_category.id
            vocabulary = Vocabulary(voc)
            vocabulary.test_category = test_category

            for op in ops:
                option = VocabularyOption({"text": op, "vocabulary_id": vocabulary.id})
                vocabulary.options.append(option)

            db.session.add(vocabulary)
        db.session.commit()
        response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response





