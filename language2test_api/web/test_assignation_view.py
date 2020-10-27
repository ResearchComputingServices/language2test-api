from language2test_api.extensions import oidc
from flask import request
from flask import json, jsonify, Response
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.test_assignation_provider import TestAssignationProvider
from language2test_api.models.test_assignation import TestAssignation, TestAssignationSchema
from language2test_api.providers.user_provider import UserProvider
from language2test_api.models.user import User

provider = TestAssignationProvider()
user_provider = UserProvider()
test_assignation_schema = TestAssignationSchema(many=False)
test_assignation_schema_many = TestAssignationSchema(many=True)


def get_authenticated_user():
    auth = request.headers.get('Authorization')
    auth_fragments = auth.split(' ')
    token = auth_fragments[1]
    user_info = oidc.user_getinfo(['preferred_username', 'given_name', 'family_name'], token)
    username = user_info['preferred_username']

    # 2 Retrieve user information
    user = User.query.filter_by(name=username).first()

    return user

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
            test_assignation = provider.update(data,test_assignation)
            result = test_assignation_schema.dump(test_assignation)
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
            provider.delete(test_assignation)
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@language2test_bp.route("/instructor/test_assignation", methods=['GET'])
@crossdomain(origin='*')
@authentication
#@authorization(['read-test'])
def get_instructor_test_assignation():
    try:
        # Retrieve user
        user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(user, 'Instructor')
        if is_instructor:
            instructor_id = user.id
            if instructor_id:
                test_assignations = provider.get_instructor_test_assignations(instructor_id)
                result = test_assignation_schema_many.dump(test_assignations)
                return jsonify(result)
            else:
                error = {"message": "No Id found for the user."}
                response = Response(json.dumps(error), 404, mimetype="application/json")
        else:
            error = {"message": "The user is not an instructor."}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response









