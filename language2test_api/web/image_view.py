from flask import request, json, Response
from werkzeug import secure_filename
import os
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.providers.image_provider import ImageProvider

provider = ImageProvider()

@language2test_bp.route("/images", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_image():
    if request.method == 'POST':
        file = request.files.get('file')
        name = request.values.get('name')
        if file and name:
            folder = 'images'
            filename = secure_filename(name)
            if not os.path.exists(folder):
                os.makedirs(folder)
            fullpath = os.path.join(folder, filename)
            file.save(fullpath)
            return Response(json.dumps([]), 201, mimetype="application/json")
    return Response(json.dumps([]), 404, mimetype="application/json")

@language2test_bp.route("/images", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_image():
    filename = request.args.get('name')
    fullpath = "images/" + filename
    if filename:
        return provider.download_file(fullpath, filename)
    return Response(json.dumps([]), 404, mimetype="application/json")

