import json
from flask import jsonify
from werkzeug.routing import RequestRedirect
from language2test_api.decorators.crossorigin import crossdomain

def create_app(package_name):
    from flask import Flask
    app = Flask(package_name)
    from language2test_api.extensions import db, ma, migrate, oidc

    with open('client_secrets.json') as client_secrets_file:
        client_secrets = json.load(client_secrets_file)

    app.config['SQLALCHEMY_DATABASE_URI'] = client_secrets.get('postgres').get('database_uri')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['USE_X_SENDFILE'] = True

    app.config.update({
        'SECRET_KEY': client_secrets.get('web').get('client_secret'),
        'TESTING': True,
        'DEBUG': True,
        'OIDC_OPENID_REALM': client_secrets.get('web').get('realm'),
        'OIDC_CLIENT_SECRETS': 'client_secrets.json',
        'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
        'OIDC_TOKEN_TYPE_HINT': 'access_token',
        'OIDC_ID_TOKEN_COOKIE_SECURE': False,
        'OIDC_REQUIRE_VERIFIED_EMAIL': False,
        #'KEYCLOAK_USERNAME' : client_secrets.get('web').get('keycloak_username')
    })

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    oidc.init_app(app)

    @app.route('/favicon.ico')
    def favi():
        return 'Hello FaviTown', 200

    return app

def register_blueprints(app):
    from language2test_api.web.views import language2test_bp
    app.register_blueprint(language2test_bp, url_prefix='/language2test_api')
    return app
