from flask import request
from flask import json, jsonify, Response
from language2test_api.models.test_type import TestType, TestTypeSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.base_provider import BaseProvider

test_type_schema = TestTypeSchema(many=False)
test_type_schema_many = TestTypeSchema(many=True)

provider = BaseProvider()

@language2test_bp.route("/test_types/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_types_count():
    return provider.get_count(TestType)

@language2test_bp.route("/test_types", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_type():
    id = request.args.get('id')
    if id:
        properties = TestType.query.filter_by(id=id).first()
        result = test_type_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = TestType.query.filter_by(name=name).first()
        result = test_type_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(TestType)
    result = test_type_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/test_types", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_test_type():
    try:
        data = request.get_json()
        test_type = TestType(data)
        db.session.add(test_type)
        db.session.commit()
        result = test_type_schema.dump(test_type)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_types", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_test_type():
    try:
        data = request.get_json()
        test_type = TestType.query.filter_by(id=data.get('id')).first()
        if not test_type:
            test_type = TestType.query.filter_by(name=data.get('name')).first()
        if test_type:
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_types", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_test_type():
    try:
        data = request.get_json()
        test_type = TestType.query.filter_by(id=data.get('id')).first()
        if not test_type:
            test_type = TestType.query.filter_by(name=data.get('name')).first()
        if test_type:
            db.session.delete(test_type)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response
