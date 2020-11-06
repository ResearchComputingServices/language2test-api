from flask import request, send_file
from flask import json, jsonify, Response
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.test_session_provider import TestSessionProvider
from language2test_api.providers.test_session_export_helper import TestSessionExportHelper as testhelper
import pandas as pd
from io import BytesIO
from language2test_api.models.test_session import TestSession, TestSessionSchema
from language2test_api.providers.test_session_export_provider import TestSessionExportProvider

test_schema = TestSessionSchema(many=False)
test_schema_many = TestSessionSchema(many=True)
provider = TestSessionProvider()
export_provider = TestSessionExportProvider()

@language2test_bp.route("/test_sessions/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_sessions_count():
    return provider.get_count(TestSession)

@language2test_bp.route("/test_sessions", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_session():
    id = request.args.get('id')
    if id:
        properties = TestSession.query.filter_by(id=int(id)).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = TestSession.query.filter_by(name=name).first()
        result = test_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(TestSession)
    result = test_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/test_sessions", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_test_session():
    try:
        data = request.get_json()
        data['id'] = provider.generate_id(field=TestSession.id)
        test_session = provider.add(data)
        db.session.commit()
        result = test_schema.dump(test_session)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_sessions", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_test_session():
    try:
        data = request.get_json()
        test_session = TestSession.query.filter_by(id=data.get('id')).first()
        if not test_session:
            test_session = TestSession.query.filter_by(name=data.get('name')).first()
        if test_session:
            if data.get('id') is None:
                data['id'] = test_session.id
            provider.update(data, test_session)
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")

    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_sessions", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_test_session():
    try:
        data = request.get_json()
        test_session = TestSession.query.filter_by(id=data.get('id')).first()
        if not test_session:
            test_session = TestSession.query.filter_by(name=data.get('name')).first()
        if test_session:
            provider.delete(data, test_session)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/test_sessions/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_test_sessions():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            name = request.args.get('name')
            if name is None:
                sessions = TestSession.query.all()
                return send_file(export_provider.write_results_into_file(sessions, name),attachment_filename='Test Details.zip',
                                mimetype="application/zip",
                                as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response


@language2test_bp.route("/instructor/test_sessions", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_sessions_for_test_assignation():
    try:
        limit = request.args.get('limit')
        offset = request.args.get('offset')

        if 'column' in request.args:
            column = request.args.get('column')
        else:
            column = 'id'

        if 'order' in request.args:
            order = request.args.get('order')
        else:
            order = 'asc'

        test_assignation_id = request.args.get('test_assignation_id')
        if test_assignation_id:
            test_sessions = provider.get_test_sessions_for_test_assignation(test_assignation_id,offset, limit, column, order)
            result = test_schema_many.dump(test_sessions)
            return jsonify(result)
        else:
            error = {"message": "Test Assignation Id expected. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")

    return response


@language2test_bp.route("/instructor/test_sessions/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_test_sessions_for_test_assignation_count():
    try:
        test_assignation_id = request.args.get('test_assignation_id')
        if test_assignation_id:
            count = provider.get_test_sessions_for_test_assignation_count(test_assignation_id)
            response = Response(json.dumps(count), 200, mimetype="application/json")
        else:
            error = {"message": "Test Assignation Id expected. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
        return response
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")

    return response

@language2test_bp.route("instructor/test_sessions/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def instructor_export_test_sessions():
    test_assignation_id = request.args.get('test_assignation_id')
    if test_assignation_id is not None:
        try:
            sessions = provider.get_test_sessions_for_test_assignation(test_assignation_id)
            name = request.args.get('name')
            return send_file(export_provider.write_results_into_file(sessions, name),attachment_filename='Test Details.zip',
                            mimetype="application/zip",
                            as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

