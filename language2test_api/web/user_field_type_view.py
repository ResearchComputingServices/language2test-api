from flask import request
from flask import json, jsonify, Response
from language2test_api.models.user_field_type import UserFieldType, UserFieldTypeSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.user_field_type_provider import UserFieldTypeProvider

user_field_type_schema = UserFieldTypeSchema(many=False)
user_field_type_schema_many = UserFieldTypeSchema(many=True)

provider = UserFieldTypeProvider()

@language2test_bp.route("/user_field_types/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_user_field_types_count():
    return provider.get_count(UserFieldType)

@language2test_bp.route("/user_field_types", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_user_field_type():
    id = request.args.get('id')
    if id:
        properties = UserFieldType.query.filter_by(id=id).first()
        result = user_field_type_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = UserFieldType.query.filter_by(name=name).first()
        result = user_field_type_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(UserFieldType)
    result = user_field_type_schema_many.dump(properties)
    return jsonify(result)


@language2test_bp.route("/user_field_types", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_user_field_type():
    try:
        data = request.get_json()
        user_field_type = provider.add(data)
        result = user_field_type_schema.dump(user_field_type)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/user_field_types", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_user_field_type():
    try:
        data = request.get_json()
        user_field_type = provider.update(data)
        if user_field_type:
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/user_field_types", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_user_field_type():
    try:
        data = request.get_json()
        user_field_type = UserFieldType.query.filter_by(id=data.get('id')).first()
        if not user_field_type:
            user_field_type = UserFieldType.query.filter_by(name=data.get('name')).first()
        if user_field_type:
            db.session.delete(user_field_type)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response
