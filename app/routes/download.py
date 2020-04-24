import flask
from flask import request, Blueprint, jsonify, send_from_directory
from actions import download as actions
from flask_cors import cross_origin

download_blueprint = Blueprint('download', __name__)

@download_blueprint.route('/', methods=["POST"])
@cross_origin()
def download():
    data = request.json['id_project'] 
    filename = actions.download(data)

    return send_from_directory('../images/zip', filename), 200