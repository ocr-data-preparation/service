import flask
from flask import request, Blueprint, jsonify

from actions import image as actions

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('/', methods=["POST"])
def addImage():
    data = request.json 
    result = actions.addImage(data)

    return jsonify(result), 201