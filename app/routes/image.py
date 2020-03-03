import flask
from flask import request, Blueprint, jsonify

from actions import image as actions

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('/', methods=["POST"])
def addImage():
    data = request.files['image'] 
    actions.saveImage(data)

    return jsonify({ "message": "success" }), 201



@image_blueprint.route('/slice', methods=["POST"])
def addImage():
    data = request.files['image'] 
    actions.saveImage(data)
    

    return jsonify({ "message": "success" }), 201