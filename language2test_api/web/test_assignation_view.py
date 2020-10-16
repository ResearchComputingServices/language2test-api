from flask import request
from flask import json, jsonify, Response
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.test_assignation_provider import TestAssignationProvider
from language2test_api.models.test_assignation import TestAssignation, TestAssignationSchema

provider = TestAssignationProvider()
test_assignation_schema = TestAssignationSchema(many=False)
test_assignation_schema_many = TestAssignationSchema(many=True)


@language2test_bp.route("/test_assignation/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
#@authorization(['read-test-assignation'])
def get_test_assignation_count():
    return provider.get_count(TestAssignation)

@language2test_bp.route("/test_assignation", methods=['GET'])
@crossdomain(origin='*')
@authentication
#@authorization(['read-test'])
def get_test_assignation():
    id = request.args.get('id')
    if id:
        properties = TestAssignation.query.filter_by(id=int(id)).first()
        result = test_assignation_schema.dump(properties)
        return jsonify(result)
    properties = provider.query_all(TestAssignation)
    result = test_assignation_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/test_assignation", methods=['POST'])
@crossdomain(origin='*')
@authentication
#@authorization(['create-test'])
def add_test_assignation():
    try:
        data = request.get_json()
        test_assignation = provider.add(data)
        result = test_assignation_schema.dump(test_assignation)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response


@language2test_bp.route("/test_assignation", methods=['PUT'])
@crossdomain(origin='*')
@authentication
#@authorization(['create-test'])
def update_test_assignation():
    try:
        data = request.get_json()
        test_assignation = TestAssignation.query.filter_by(id=data.get('id')).first()
        if test_assignation:
            result = provider.update(data,test_assignation)
            response = Response(json.dumps(result), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_assignation", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
#@authorization(['delete-student-class'])
def delete_test_assignation():
    try:
        data = request.get_json()
        test_assignation = TestAssignation.query.filter_by(id=data.get('id')).first()
        if test_assignation:
            db.session.delete(test_assignation)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response








