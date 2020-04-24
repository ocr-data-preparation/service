import flask
from flask import Flask, jsonify, send_from_directory
from flask_cors import cross_origin
from datetime import datetime
import os

import config
from routes.image import image_blueprint
from routes.project import create_project_blueprint
from routes.download import download_blueprint

app = Flask(__name__)

app.register_blueprint(image_blueprint, url_prefix='/image')
app.register_blueprint(download_blueprint, url_prefix='/download')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/db.sqlite')
create_project_blueprint(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response

@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def get():
    current_time = datetime.now()
    return jsonify({"time": current_time })

@app.route('/images/<path:filename>', methods=['GET'])
@cross_origin()
def download_file(filename):
    return send_from_directory('../images', filename)

app.run(port = config.PORT)

