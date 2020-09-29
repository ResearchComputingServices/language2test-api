from language2test_api.web.views import *
from language2test_api import language2test_factory

global app

app = language2test_factory.create_app(__name__)
app.app_context().push()
language2test_factory.register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=7017)

