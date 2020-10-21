from flask import request
from flask import json, jsonify, Response
from language2test_api.models.user import User, UserSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.test_schedule_provider import TestScheduleProvider

from language2test_api.extensions import oidc


provider = TestScheduleProvider()

@language2test_bp.route('/test_schedule', methods=['GET'])
@crossdomain(origin='*')
@authentication
#@authorization(['create-user'])
def test_schedule():
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
            result = provider.get_schedule(user.id, start_datetime_rq, end_datetime_rq)
            response = jsonify(result)
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response
