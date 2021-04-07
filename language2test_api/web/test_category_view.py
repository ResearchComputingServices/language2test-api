from flask import request, jsonify, url_for, Blueprint, send_file
from flask import json, jsonify, Response, blueprints
from language2test_api.models.test_category import TestCategory, TestCategorySchema
from language2test_api.models.test_type import TestType, TestTypeSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.test_category_provider import TestCategoryProvider
import pandas as pd
from io import BytesIO
from language2test_api.models.test_session import TestSession, TestSessionSchema

test_category_schema = TestCategorySchema(many=False)
test_category_schema_many = TestCategorySchema(many=True)

provider = TestCategoryProvider()

test_schema = TestSessionSchema(many=False)
test_schema_many = TestSessionSchema(many=True)

@language2test_bp.route("/test_categories/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_categories_count():
    return provider.get_count(TestCategory)

@language2test_bp.route("/test_categories", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_category():
    id = request.args.get('id')
    if id:
        properties = TestCategory.query.filter_by(id=int(id)).first()
        result = test_category_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    type = request.args.get('type')
    if name and not type:
        properties = TestCategory.query.filter_by(name=name)
        result = test_category_schema_many.dump(properties)
        return jsonify(result)

    if name and type:
        type_properties = TestType.query.filter_by(name=type).first()
        test_type_id = type_properties.id
        properties = TestCategory.query.filter(TestCategory.name == name).filter(TestCategory.test_type_id == test_type_id).first()
        result = test_category_schema.dump(properties)
        return jsonify(result)

    if not name and type:
        type_properties = TestType.query.filter_by(name=type).first()
        test_type_id = type_properties.id
        properties = TestCategory.query.filter(TestCategory.test_type_id == test_type_id)
        result = test_category_schema_many.dump(properties)
        return jsonify(result)

    properties = provider.query_all(TestCategory)
    result = test_category_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/test_categories", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_test_category():
    try:
        data = request.get_json()
        test = provider.add(data)
        db.session.add(test)
        db.session.commit()
        result = test_category_schema.dump(test)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_categories", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_test_category():
    try:
        data = request.get_json()
        test_category = TestCategory.query.filter_by(id=data.get('id')).first()
        if not test_category:
            test_category = TestCategory.query.filter_by(name=data.get('name')).first()
        if test_category:
            provider.update(data, test_category)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_categories", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_test_category():
    try:
        data = request.get_json()
        test = TestCategory.query.filter_by(id=data.get('id')).first()
        if not test:
            test = TestCategory.query.filter_by(name=data.get('name')).first()
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


@language2test_bp.route("/test_categories/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_test_categories():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            categories = TestCategory.query.all()
            for c in categories:
                records.append({
                    "Id": c.id,
                    "Name": c.name,
                    "Type": c.test_type.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="{} summary".format('test_category'),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format('test_category')]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:B', 15, format)
                worksheet.set_column('C:C', 20, format)
                writer.save()
            output.seek(0)
            return send_file(output,
                             attachment_filename="Test Category Summary" + '.xlsx',
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
                tc_id = request.args.get('id')
                tc = TestCategory.query.filter_by(id=tc_id).first()
                result = test_category_schema.dump(tc)
                name = tc.name
            if name is not None:
                tc = TestCategory.query.filter_by(id=tc_id).first()
                result = test_category_schema.dump(tc)
            tc_infos = {
                "Id": result['id'],
                "Name": result['name'],
                "Type": result['test_type']['name']
            }

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame([tc_infos]).to_excel(writer,
                                               sheet_name="{} details".format("Test Category"),
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} details".format("Test Category")]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:C', 15, format)
                writer.save()
            output.seek(0)
            return send_file(output,
                             attachment_filename="Test Category" + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

