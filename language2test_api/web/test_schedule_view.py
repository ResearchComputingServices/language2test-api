from flask import request
from flask import json, jsonify, Response
from language2test_api.models.user import User, UserSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.test_schedule_provider import TestScheduleProvider
from language2test_api.providers.user_provider import UserProvider
from language2test_api.models.test_assignation import TestAssignationSchema

from language2test_api.extensions import oidc


provider = TestScheduleProvider()
user_provider = UserProvider()
test_assignation_schema_many = TestAssignationSchema(many=True)

@language2test_bp.route('/test_schedule/test_taker', methods=['GET'])
@crossdomain(origin='*')
@authentication
def test_schedule_test_taker():
    auth = request.headers.get('Authorization')
    auth_fragments = auth.split(' ')
    token = auth_fragments[1]
    try:
        user_info = oidc.user_getinfo(['preferred_username', 'given_name', 'family_name'], token)
        name = user_info['preferred_username']
        user = User.query.filter_by(name=name).first()
        start_datetime_rq = request.args.get('start_datetime')
        end_datetime_rq = request.args.get('end_datetime')
        if user:
            result = provider.get_test_taker_schedule(user.id, start_datetime_rq, end_datetime_rq)
            response = jsonify(result)
        else:
            message = {"message": "User does not exist. Check the format of the request."}
            response = Response(json.dumps(message), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response



@language2test_bp.route('/test_schedule/instructor', methods=['GET'])
@crossdomain(origin='*')
@authentication
def test_schedule_instructor():
    try:
        # Retrieve user
        start_datetime_rq = request.args.get('start_datetime')
        end_datetime_rq = request.args.get('end_datetime')
        user = user_provider.get_authenticated_user()
        is_instructor = user_provider.has_role(user, 'Instructor')
        if is_instructor:
            instructor_id = user.id
            if instructor_id:
                test_assignations = provider.get_instructor_test_schedule(user.id, start_datetime_rq, end_datetime_rq)
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
