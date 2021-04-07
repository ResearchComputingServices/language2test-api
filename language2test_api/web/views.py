from flask import request, jsonify, url_for, Blueprint
from flask import json, jsonify, Response, blueprints
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
import language2test_api.web.role_view
import language2test_api.web.user_view
import language2test_api.web.vocabulary_view
import language2test_api.web.test_session_view
import language2test_api.web.rc_view
import language2test_api.web.cloze_view
import language2test_api.web.cloze_question_correctly_typed_view
import language2test_api.web.cloze_question_incorrectly_typed_view
import language2test_api.web.cloze_question_pending_typed_view
import language2test_api.web.test_view
import language2test_api.web.image_view
import language2test_api.web.test_type_view
import language2test_api.web.test_category_view
import language2test_api.web.user_field_type_view
import language2test_api.web.user_field_category_view
import language2test_api.web.student_class_view
import language2test_api.web.writing_view
import language2test_api.web.enumeration_view
import language2test_api.web.user_keycloak
import language2test_api.web.authorization_view
import language2test_api.web.test_assignation_view
import language2test_api.web.test_schedule_view


@language2test_bp.route("/", methods=['GET'])
@crossdomain(origin='*')
@authentication
def hello():
    return "Hello Language2Test!"

