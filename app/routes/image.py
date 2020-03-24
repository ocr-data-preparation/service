import flask
import json
from flask import request, Blueprint, jsonify
import os
from numpy import flip, array
from datetime import datetime
from actions import image as actions
from actions import scan as scan
from PIL import Image


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

@image_blueprint.route('/save', methods=["POST"])
def bulk_save_image():
    path = request.json['path']
    excludes = request.json['excludes']
    pixels = request.json['pixels']

    actions.bulk_save(path, excludes, pixels)
    
    return jsonify({ "message" : "success" }), 200

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

@image_blueprint.route('/submit', methods=["POST"])
def submit():
    data = request.files['image']

    filename = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

    path = os.path.join("images/", filename + ".jpg")
    data.save(path)
    #cropping image
    img = scan.parse_image("images/" + filename + ".jpg")               
    pil_img = Image.fromarray(array([[flip(element) for element in row] for row in img])) 

    #generate data for return        
    image, image_list, bool_list = actions.create_connected_component(pil_img)
    squared_path = 'images/squared/' + filename + '.jpg'
    actions.save_image_cv(image, squared_path)

    return jsonify({ "squared_image_path":  squared_path, "path": path, "excludes": bool_list}), 200   
