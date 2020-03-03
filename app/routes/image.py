import flask
from flask import request, Blueprint, jsonify
from actions import image as actions
import os
from datetime import datetime

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('/', methods=["POST"])
def addImage():
    data = request.files['image'] 
    actions.saveImage(data)

    return jsonify({ "message": "success" }), 201

@image_blueprint.route('/slice', methods=["POST"])
def sliceIm():
    data = request.files['image'] 
    current_time = datetime.now()
    actions.imageSlicer(data,os.getcwd(),current_time)

    return jsonify({ "message": "success" }), 201

@image_blueprint.route('/detect/blank', methods=["POST"])
def detectBlank():
    data = request.files['image'] 
    is_blank = actions.isBlank(data)

    return jsonify({ "is_blank" : is_blank }), 201
