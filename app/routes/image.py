import flask
from flask import request, Blueprint, jsonify
import os
from datetime import datetime

from actions import image as actions

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('/', methods=["POST"])
def add_image():
    data = request.files['image'] 
    actions.save_image(data)

    return jsonify({ "message": "success" }), 200

@image_blueprint.route('/slice', methods=["POST"])
def slice_image():
    data = request.files['image'] 
    current_time = datetime.now()
    actions.slice_image(data)

    return jsonify({ "message": "success" }), 200

@image_blueprint.route('/detect/blank', methods=["POST"])
def detect_blank():
    data = request.files['image'] 
    is_blank = actions.is_blank(data)

    return jsonify({ "is_blank" : is_blank }), 200

@image_blueprint.route('/cc', methods=["POST"])
def create_connected_component():
    data = request.files['image'] 
    image, image_list, bool_list = actions.create_connected_component(data)
    actions.save_image_cv(image, 'images/test/image.jpg')
    for i, row in enumerate(image_list):
        for j, element in enumerate(row):
            blank = str(bool_list[i][j])
            actions.save_image_cv(element, 'images/test/' + str(i) + '/' + blank + str(j) + '.jpg')

    return jsonify({ "message": "success" }), 200   