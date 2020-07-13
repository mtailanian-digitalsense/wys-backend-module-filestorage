from flask import Flask, jsonify, abort, \
    request, flash, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime as dt
import logging
import base64 as b64
import jwt
from functools import wraps
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from http import HTTPStatus

import os

app = Flask(__name__)

FS_LOCATION_PATH = os.getenv('FS_LOCATION_PATH', '.')
FS_DNS_URL = os.getenv('FS_DNS_URL', 'http://127.0.0.1:5000')
FILE_URL = '/api/filestorage/'
app.config['UPLOAD_FOLDER'] = FS_LOCATION_PATH
CORS(app)

try:
    f = open('oauth-public.key', 'r')
    key: str = f.read()
    f.close()
    app.config['SECRET_KEY'] = key
except Exception as e:
    app.logger.error(f'Can\'t read public key f{e}')
    exit(-1)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        bearer_token = request.headers.get('Authorization', None)
        try:
            token = bearer_token.split(" ")[1]
        except Exception as ierr:
            app.logger.error(ierr)
            abort(jsonify({'message': 'a valid bearer token is missing'}), 500)

        if not token:
            app.logger.debug("token_required")
            return jsonify({'message': 'a valid token is missing'})

        app.logger.debug("Token: " + token)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['RS256'], audience="1")
            user_id: int = data['user_id']
            request.environ['user_id'] = user_id
        except Exception as err:
            return jsonify({'message': 'token is invalid', 'error': err})
        except KeyError as kerr:
            return jsonify({'message': 'Can\'t find user_id in token', 'error': kerr})

        return f(*args, **kwargs)

    return decorator


SWAGGER_URL = '/api/filestorage/docs/'
API_URL = '/api/filestorage/spec'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "WYS Api. Project Service"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/api/filestorage/spec", methods=['GET'])
@token_required
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "WYS File Storage API Service"
    swag['tags'] = [{
        "name": "Filestorage",
        "description": "Methods to save and get files"
    }]
    return jsonify(swag)


@app.route('/api/filestorage/save', methods=['POST'])
@token_required
def save_file():
    """
        Save a new file
        ---
        tags:
        - "Filestorage"
        produces:
        - "application/json"
        consumes:
        - "multipart/form-data"
        parameters:
        - name: "file"
          in: "formData"
          description: "File to upload"
          required: true
          type: file
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        abort(HTTPStatus.BAD_REQUEST, "No Multipart file found")
    file = request.files['file']

    if file.filename == '':
        flash('No selected File')
        abort(HTTPStatus.NOT_FOUND, "No selected file")
    encoding = "utf-8"
    filename: str = secure_filename(file.filename)
    filename_ext: str = filename + str(dt.timestamp(dt.utcnow()))
    filename_coded: str = b64.b64encode(filename_ext.encode(encoding)).decode(encoding)
    ext = ""
    if len(filename.split('.')) > 1:
        ext = "." + filename.split('.')[-1]
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_coded + ext))
    dict_ret = {
        'url': FS_DNS_URL + FILE_URL + filename_coded + ext
    }
    file.close()
    return jsonify(dict_ret), HTTPStatus.CREATED


@app.route(FILE_URL + '<filename>', methods=['GET'])
def get_file(filename: str):
    """
        Get a file saved in this service
        ---

        tags:
        - "Filestorage"
        produces:
        - "application/json"
        consumes:
        - "multipart/form-data"
        parameters:
        - in: "path"
          name: "filename"
          description: "Filename to download"
          required: true
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route(FILE_URL + '<filename>', methods=['PUT'])
@token_required
def update_file(filename: str):
    """
        Update a file
        ---

        tags:
        - "Filestorage"
        parameters:
        - in: "path"
          name: "filename"
          description: "Filename to update"
          required: true
        - name: "file"
          in: "formData"
          description: "File to upload"
          required: true
          type: file
        responses:
          200:
            description: Update successfully
          404:
            description: "File not found"
          500:
            description: "Internal Error"

    """
    # Check if file exist
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(path):
        err = {'msg': f"{filename} File not found"}
        logging.warning(err['msg'])
        abort(HTTPStatus.NOT_FOUND, jsonify(err))

    try:
        # Save file
        file = request.files['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.close()
        dict_ret = {
            'url': FS_DNS_URL + FILE_URL + filename
        }
        return jsonify(dict_ret)

    except Exception as ex:
        err = {
            'msg': f"Can't update file {filename}",
            'err': ex
        }
        logging.warning(err)
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, jsonify(err))


if __name__ == '__main__':
    app.run(debug=True)
