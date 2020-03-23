from __future__ import division
import flask
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import math
from random import seed
from random import randint
import cv2 as cv
import numpy as np
import copy

N_ROW = 10
N_COLLUMN = 14
SQUARE_MARGIN_DIVISION_FACTOR = 10
CONNECTED_COMPONENT_OFFSET = 3
APPEND_WHITE_DIVISION_FACTOR = 16
MINIMUM_APPEND_COLOR = 192

def save_image(image):
    current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
    filename = secure_filename(current_time)

    path = os.path.join("images/", filename + ".jpg")
    image.save(path)

    return path

def is_blank(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _,th = cv.threshold(image,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    count0 = cv.countNonZero(th)
    countTotal = th.shape[0] * th.shape[1]
    white_percentage = count0/countTotal

    if white_percentage  > 0.999:
        return True
    else:
        return False

def slice_image(image):
    path = save_image(image)

    img = Image.open(path)
    img_size = img.size
    width, height = img.size

    upper = 0
    slice_size_vert = float(height/N_ROW)
    slice_size_horz = float(width/N_COLLUMN)

    row_slices = N_ROW
    collumn_slices = N_COLLUMN

    # count = 1
    slice_list = []
    for x in range(row_slices):
        left = 0
        
        row_slice_list = []
        for y in range(collumn_slices): 
            
            bbox = (round(left + slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR), round(upper + slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR), round(left + slice_size_horz - slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR), round(upper + slice_size_vert - slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR))
            temp_working_slice = img.crop(bbox)
            
            numpy_image = np.array(temp_working_slice)  

            working_slice = cv.cvtColor(numpy_image, cv.COLOR_RGB2BGR)  

            row_slice_list.append(working_slice)

            # current_time = datetime.now().strftime(str(y) + " - %d-%b-%Y (%H:%M:%S)")
            # filename = secure_filename(current_time)
            # working_path = os.path.join("images/"+ str((x+1)%10) +"/", filename + ".jpg")

            # temp_working_slice.save(working_path)
            
            # count +=1
            left += slice_size_horz

        slice_list.append(row_slice_list)
        upper += slice_size_vert
    
    numpy_img = np.array(img) 
    img = cv.cvtColor(numpy_img, cv.COLOR_RGB2BGR)

    return img, slice_list, img_size

def bulk_save(path, excludes, pixels):
    img = Image.open(path)
    
    image, result_image_list, boolean_list = create_connected_component(img)

    for i, row in enumerate(result_image_list):
        for j, im in enumerate(row):
            if not excludes[i][j]:
                im = cv.resize(im, (pixels, pixels))
                current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S) " + str(j))
                save_image_cv(im, "images/"+ str((i+1)%10) + "/" + current_time + ".jpg")

#resize image: tambahin ke tempat ingin dipakai
def resize(x):
    # Opens a image in RGB mode  
    im = Image.open(r"file[ath")  
  
    newsize = (x, x) 
    im1 = im1.resize(newsize) 
    # Shows the image in image viewer  
    im1.show() 

def remove_borders(image):
    for i, row in enumerate(image):
        for j, _ in enumerate(row):
            if i == 0 or j == 0 or i == len(image) - 1 or j == len(image[0]) - 1:
                cv.floodFill(image, None, seedPoint=(j,i), newVal=[255, 255, 255], loDiff=(50, 50, 50, 50), upDiff=(50, 50, 50, 50))
    return image

def get_corner(component_list):
    x1 = -1
    x2 = -1
    y1 = -1
    y2 = -1
    for i, row in enumerate(component_list):
        for j, element in enumerate(row):
            if element == 0:
                if x1 == -1 or j < x1:
                    x1 = j
                if x2 == -1 or j > x2:
                    x2 = j
                if y1 == -1 or i < y1:
                    y1 = i
                if y2 == -1 or i > y2:
                    y2 = i
    return x1 - CONNECTED_COMPONENT_OFFSET, x2 + CONNECTED_COMPONENT_OFFSET, y1 - CONNECTED_COMPONENT_OFFSET, y2 + CONNECTED_COMPONENT_OFFSET


def get_connected_component_corners(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _,th = cv.threshold(image,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    num_labels, labels_im = cv.connectedComponents(th)
    return get_corner(labels_im)


def get_border_color(connected_component_img):
    color = [0, 0, 0]
    count = 0
    for i, row in enumerate(connected_component_img):
        for j, element in enumerate(row):
            if i == 0 or j == 0 or i == len(connected_component_img) - 1 or j == len(connected_component_img[0]) - 1:
                element_color_mean = int((int(element[0]) + int(element[1]) + int(element[2])) / 3)
                if element_color_mean > MINIMUM_APPEND_COLOR:
                    color[0] += element[0]
                    color[1] += element[1]
                    color[2] += element[2]
                    count += 1
    if count > 0:
        return [int(color[0] / count), int(color[1] / count), int(color[2] / count)]
    else:
        return[MINIMUM_APPEND_COLOR, MINIMUM_APPEND_COLOR, MINIMUM_APPEND_COLOR]


def append_white(connected_component_img):
    image_length = len(connected_component_img[0])
    image_width = len(connected_component_img)
    x_border_size = 0
    y_border_size = 0
    not_enough = ''
    border_color = get_border_color(connected_component_img)
    if image_length > image_width:
        x_border_size = round(image_length / APPEND_WHITE_DIVISION_FACTOR)
        y_border_size = round((image_length - image_width + 2 * x_border_size) / 2)
    else:
        y_border_size = round(image_width / APPEND_WHITE_DIVISION_FACTOR)
        x_border_size = round((image_width - image_length + 2 * y_border_size) / 2)
    
    if image_length + 2 * x_border_size < image_width + 2 * y_border_size:
        not_enough = 'length'
        connected_component_img = cv.copyMakeBorder(np.array(connected_component_img), y_border_size, y_border_size,
        x_border_size, x_border_size + 1, cv.BORDER_CONSTANT, value=border_color)
    
    elif image_length + 2 * x_border_size > image_width + 2 * y_border_size:
        not_enough = 'width' 
        connected_component_img = cv.copyMakeBorder(np.array(connected_component_img), y_border_size, y_border_size + 1,
        x_border_size, x_border_size, cv.BORDER_CONSTANT, value=border_color)
    
    else:
        connected_component_img = cv.copyMakeBorder(np.array(connected_component_img), y_border_size, y_border_size,
        x_border_size, x_border_size, cv.BORDER_CONSTANT, value=border_color)

    image_length = len(connected_component_img[0])
    image_width = len(connected_component_img)
    if image_length != image_width:
        raise Exception("AppendError")
    
    return connected_component_img, x_border_size, y_border_size, not_enough

def insert_into_image(image, content, xstart, ystart):
    for i, row in enumerate(content):
        for j, element in enumerate(row):
            try:
                image[ystart + i][xstart + j] = element
            except IndexError:
                continue
    return image

def check_insert_image(image, content, xstart, ystart):
    for i, row in enumerate(content):
        for j, element in enumerate(row):
            try:
                if (image[ystart + i][xstart + j].all() != element.all()):
                    raise Exception('InsertError')
            except IndexError:
                continue

def create_connected_component(image):
    original_image, slice_list, size = slice_image(image)
    width, height = size

    image = copy.deepcopy(original_image)

    upper = 0
    slice_size_vert = round(height/N_ROW)
    slice_size_horz = round(width/N_COLLUMN)

    boolean_list = []
    result_image_list = []
    for i, row in enumerate(slice_list):
        
        row_boolean_list = []
        row_result_image_list = []
        left = 0

        for j, slice_element in enumerate(row):
            if is_blank((slice_element)):
                row_boolean_list.append(False)
                
                x1 = round(left + slice_size_horz / 8)
                x2 = round(left +  slice_size_horz * 7 / 8)
                y1 = round(upper + slice_size_vert / 8) 
                y2 = round(upper + slice_size_vert * 7 / 8)
                
                cv.rectangle(image, (x1-1, y1-1),  (x2+1, y2+1), (0, 0, 255), 1)
                row_result_image_list.append([row[x1:x2+1] for row in original_image][y1:y2+1])

            else:
                row_boolean_list.append(True)
        
                x1, x2, y1, y2 = get_connected_component_corners((slice_element)) 
                x1 += round(left + slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR)
                x2 += round(left + slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR)
                y1 += round(upper + slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR) 
                y2 += round(upper + slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR)
                
                connected_component_img = [row[x1:x2+1] for row in original_image][y1:y2+1]
                
                connected_component_img, x_border_size, y_border_size, not_enough = append_white(connected_component_img)
                
                x1 -= x_border_size
                x2 += x_border_size
                y1 -= y_border_size
                y2 += y_border_size
                if not_enough == 'length':
                    x2 += 1
                elif not_enough == 'width':
                    y2 += 1 
                cv.rectangle(image, (x1-1, y1-1), (x2+1, y2+1), (0, 255, 0), 1)
                image = insert_into_image(image, connected_component_img, x1, y1)
                check_insert_image(image, connected_component_img, x1, y1)
                row_result_image_list.append(connected_component_img)

            left = left + slice_size_horz

        upper = upper + slice_size_vert
        boolean_list.append(row_boolean_list)
        result_image_list.append(row_result_image_list)
    
    return image, result_image_list, boolean_list

def save_image_cv(image, path):
    cv.imwrite(path, np.array(image))
