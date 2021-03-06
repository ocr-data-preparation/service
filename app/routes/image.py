import flask
import json
from flask import request, Blueprint, jsonify
import os
from numpy import flip, array
from datetime import datetime
from actions import image as actions
from actions import scan as scan
from flask_cors import cross_origin
from PIL import Image

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('/', methods=["POST"])
@cross_origin()
def add_image():
    data = request.files['image'] 
    actions.save_image(data)

    return jsonify({ "message": "success" }), 200

@image_blueprint.route('/slice', methods=["POST"])
@cross_origin()
def slice_image():
    data = request.files['image'] 
    current_time = datetime.now()
    actions.slice_image(data)

    return jsonify({ "message": "success" }), 200

@image_blueprint.route('/detect/blank', methods=["POST"])
@cross_origin()
def detect_blank():
    data = request.files['image'] 
    is_blank = actions.is_blank(data)

    return jsonify({ "is_blank" : is_blank }), 200


@image_blueprint.route('/save/color', methods=["POST"])
@cross_origin()
def bulk_save_image_color():
    path = request.json['path']
    includes = request.json['includes']
    pixels = request.json['pixels']
    slice_type = request.json['slice_type']
    project_id = request.json['project']
    padding = request.json['padding']

    actions.bulk_save(path, project_id, includes, pixels, slice_type, True, padding=padding)
    
    return jsonify({ "message" : "success" }), 200

@image_blueprint.route('/save/blackwhite', methods=["POST"])
@cross_origin()
def bulk_save_image_blackwhite():
    path = request.json['path']
    includes = request.json['includes']
    pixels = request.json['pixels']
    slice_type = request.json['slice_type']
    thickness = request.json['thickness']
    denoise_type = request.json['denoise_type']
    window_size = request.json['window_size']
    project_id = request.json['project']
    padding = request.json['padding']

    actions.bulk_save(path, project_id, includes, pixels, slice_type, False, thickness=thickness, denoise_type=denoise_type, window_size=window_size, padding=padding)
    
    return jsonify({ "message" : "success" }), 200

# endpoint clean directory
@image_blueprint.route('/clean', methods=["POST"])
@cross_origin()
def clean_directory():
    actions.clean_dir()
    return jsonify({ "message" : "success" }), 200

@image_blueprint.route('/cc', methods=["POST"])
@cross_origin()
def create_connected_component():
    data = request.files['image']
    image, image_list, bool_list = actions.create_connected_component_slices(data)
    actions.save_image_cv(image, 'images/test/image.jpg')
    for i, row in enumerate(image_list):
        for j, element in enumerate(row):
            blank = str(bool_list[i][j])
            actions.save_image_cv(element, 'images/test/' + str(i) + '/' + blank + str(j) + '.jpg')

    return jsonify({ "message": "success" }), 200   

@image_blueprint.route('/submit', methods=["POST"])
@cross_origin()
def submit():
    data = request.files['image']

    filename = datetime.now().strftime("%d-%b-%Y-(%H-%M-%S)")

    path = os.path.join("images/", filename + ".jpg")
    data.save(path)
    #cropping image
    img = scan.parse_image("images/" + filename + ".jpg")
    height = img.shape[0]
    width = img.shape[1]
    img2 = scan.parse_image(img)
    if(img2.shape[0] > 0.5*height or img2.shape[1] > 0.5*width):
        img = img2
    actions.make_directories("images/standardized")
    path = "images/standardized/" + filename + ".jpg"
    actions.save_image_cv(img, path)           
    pil_img = Image.fromarray(array([[flip(element) for element in row] for row in img])) 

    #generate data for return        
    image, image_list, bool_list = actions.create_connected_component_slices(pil_img, True)
    actions.make_directories("images/squared")
    squared_path = 'images/squared/' + filename + '.jpg'
    actions.save_image_cv(image, squared_path)

    return jsonify({ "squared_image_path":  squared_path, "path": path, "excludes": bool_list}), 200   

@image_blueprint.route('/change/color', methods=["POST"])
@cross_origin()
def change_color():
    path = request.json['path']
    slice_type = request.json['slice_type']
    padding = request.json['padding']

    img = Image.open(path)

    #generate data for return        
    if  (slice_type == 'box'):
        image, image_list, bool_list = actions.create_box_slices(img, True)
    elif (slice_type == 'number'):
        image, image_list, bool_list = actions.create_connected_component_slices(img, True, padding=padding)

    filename = datetime.now().strftime("%d-%b-%Y-(%H-%M-%S)")
    squared_path = 'images/squared/' + filename + '.jpg'
    actions.save_image_cv(image, squared_path)

    return jsonify({ "squared_image_path":  squared_path, "includes": bool_list}), 200  

@image_blueprint.route('/change/blackwhite', methods=["POST"])
@cross_origin()
def change_blackwhite():
    path = request.json['path']
    slice_type = request.json['slice_type']
    thickness = request.json['thickness']
    denoise_type = request.json['denoise_type']
    window_size = request.json['window_size']
    padding = request.json['padding']
    
    img = Image.open(path)

    #generate data for return        
    if  (slice_type == 'box'):
        image, image_list, bool_list = actions.create_box_slices(img, False, thickness=thickness, denoise_type=denoise_type, window_size=window_size)
    elif (slice_type == 'number'):
        image, image_list, bool_list = actions.create_connected_component_slices(img, False, thickness=thickness, denoise_type=denoise_type, window_size=window_size, padding=padding)

    filename = datetime.now().strftime("%d-%b-%Y-(%H-%M-%S)")
    squared_path = 'images/squared/' + filename + '.jpg'
    actions.save_image_cv(image, squared_path)

    return jsonify({ "squared_image_path":  squared_path, "includes": bool_list}), 200   

@image_blueprint.route("/statistic",methods=["POST"])
@cross_origin()
def statistic():
    project = request.json["project"]
    statistic = actions.project_statistic(project)
    return jsonify([
                {   "id": 0,
                    "amount":statistic[0]}
                ,{  "id": 1,
                    "amount":statistic[1]}
                ,{  "id": 2,
                    "amount":statistic[2]}
                ,{  "id": 3,
                    "amount":statistic[3]}
                ,{  "id": 4,
                    "amount":statistic[4]}
                ,{  "id": 5,
                    "amount":statistic[5]}
                ,{  "id": 6,
                    "amount":statistic[6]}
                ,{  "id": 7,
                    "amount":statistic[7]}
                ,{  "id": 8,
                    "amount":statistic[8]}
                ,{  "id": 9,
                    "amount":statistic[9]} 
            ])
