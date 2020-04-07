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
import imutils


N_ROW = 10
N_COLLUMN = 14
SQUARE_MARGIN_DIVISION_FACTOR = 12
CONNECTED_COMPONENT_STARTING_OFFSET = 0 # Minimum start of connected component
CONNECTED_COMPONENT_DEVIATION = 0 # Deviation added to connected component
APPEND_WHITE_DIVISION_FACTOR = 16
MINIMUM_APPEND_COLOR = 192

def save_image(image):
    current_time = datetime.now().strftime("%d-%b-%Y (%H-%M-%S)")
    filename = secure_filename(current_time)

    path = os.path.join("images/", filename + ".jpg")
    image.save(path)

    return path

def is_blank(image, color):
    if color:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        _,th = cv.threshold(image,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    else:
        th = image
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
    # baru
    bboxes = split_by_box(path)
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
            # baru
            # bbox = (round(left + slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR), round(upper + slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR), round(left + slice_size_horz - slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR), round(upper + slice_size_vert - slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR))
            bbox = bboxes[x][y]
            temp_working_slice = img.crop(bbox)
            
            numpy_image = np.array(temp_working_slice)  

            working_slice = cv.cvtColor(numpy_image, cv.COLOR_RGB2BGR)  

            row_slice_list.append(working_slice)

            left += slice_size_horz

        slice_list.append(row_slice_list)
        upper += slice_size_vert
    
    numpy_img = np.array(img) 
    img = cv.cvtColor(numpy_img, cv.COLOR_RGB2BGR)
    slice_border = [[{'left' : round(slice_size_horz * j + slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR), \
                    'up' : round(slice_size_vert * i + slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR), \
                    'right' : round(slice_size_horz * (j + 1) - slice_size_horz / SQUARE_MARGIN_DIVISION_FACTOR), \
                    'down' : round(slice_size_vert * (i + 1) - slice_size_vert / SQUARE_MARGIN_DIVISION_FACTOR)} \
                    for j in range(collumn_slices)] for i in range(row_slices)]

    return img, slice_list, img_size, slice_border

def bulk_save(path, project_id, includes, pixels, slice_type,  color, **kwargs):
    img = Image.open(path)
    
    if slice_type == 'box':
        if color:
            image, result_image_list, boolean_list = create_box_slices(img, color)
        else:
            image, result_image_list, boolean_list = create_box_slices(img, color, \
                thickness=kwargs.get('thickness', 1), denoise_type=kwargs.get('denoise_type', 'none'), window_size=kwargs.get('window_size', 21))
    elif slice_type == 'number':
        if color:
            image, result_image_list, boolean_list = create_connected_component_slices(img, color)
        else:    
            image, result_image_list, boolean_list = create_connected_component_slices(img, color, \
                thickness=kwargs.get('thickness', 1), denoise_type=kwargs.get('denoise_type', 'none'), window_size=kwargs.get('window_size', 21))

    # BIKIN DIREKTORI BUAT TIAP PROJECT
    project_dir = "images/" + project_id
    make_directories(project_dir)

    for i, row in enumerate(result_image_list):
        for j, im in enumerate(row):
            if includes[i][j]:
                im = cv.resize(im, (pixels, pixels))
                current_time = datetime.now().strftime("%d-%b-%Y (%H-%M-%S) " + str(j))

                # bikin direktori buat folder tiap angka
                images_dir = project_dir + "/" + str((i)%10)
                make_directories(images_dir)
                
                # save gambar ke folder masing masing
                image_filename = images_dir + "/" + current_time + ".jpg"
                save_image_cv(im, image_filename)

# FUNGSI BUAT BIKIN DIREKTORI
def make_directories(dirName):
    try:
        os.makedirs(dirName)    
        print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")

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

def get_points(component_list, size_list):
    x1 = -1
    x2 = -1
    y1 = -1
    y2 = -1
    label = np.argmax(size_list[1:]) + 1
    for i, row in enumerate(component_list):
        for j, element in enumerate(row):
            if element == label:
                if x1 == -1 or j < x1:
                    x1 = j
                if x2 == -1 or j > x2:
                    x2 = j
                if y1 == -1 or i < y1:
                    y1 = i
                if y2 == -1 or i > y2:
                    y2 = i
    return max(x1 - round(CONNECTED_COMPONENT_DEVIATION * len(component_list[0])), round(CONNECTED_COMPONENT_STARTING_OFFSET * len(component_list[0]))), \
    min(x2 + round(CONNECTED_COMPONENT_DEVIATION * len(component_list[0])), round((1 - CONNECTED_COMPONENT_STARTING_OFFSET) * len(component_list[0])) - 1),  \
    max(y1 - round(CONNECTED_COMPONENT_DEVIATION * len(component_list)), round(CONNECTED_COMPONENT_STARTING_OFFSET * len(component_list))), \
    min(y2 + round(CONNECTED_COMPONENT_DEVIATION * len(component_list)), round((1 - CONNECTED_COMPONENT_STARTING_OFFSET) * len(component_list)) - 1)


def get_connected_component_corners(image, color):
    if color:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        _, th = cv.threshold(image,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        _, labels_im, stats, _ = cv.connectedComponentsWithStats(cv.bitwise_not(th))
    else:
        _, labels_im, stats, _ = cv.connectedComponentsWithStats(cv.bitwise_not(image))
    return get_points(labels_im, stats[:, -1])


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


def append_white(connected_component_img, color):
    image_length = len(connected_component_img[0])
    image_width = len(connected_component_img)
    x_border_size = 0
    y_border_size = 0
    not_enough = ''
    
    if color:
        border_color = get_border_color(connected_component_img)
    else:
        border_color = 255

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

def insert_into_image(image, content, xstart, ystart, color):
    for i, row in enumerate(content):
        for j, element in enumerate(row):
            try:
                if color:
                    image[ystart + i][xstart + j] = element
                else:
                    image[ystart + i][xstart + j] = [element, element, element]
            except IndexError:
                continue
    return image

def convert_to_black_white(image, slice_list):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(image,(5,5),0)
    _, image = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    for i in range(len(slice_list)):
        for j in range(len(slice_list[i])):
            slice_list[i][j] = cv.cvtColor(slice_list[i][j], cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(slice_list[i][j],(5,5),0)
            _, slice_list[i][j] = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    return image, slice_list


def denoise_list(slice_list, type, **kwargs):
    for i in range(len(slice_list)):
        for j in range(len(slice_list[i])):
            if type == 'auto':
                slice_list[i][j] = denoising(slice_list[i][j])
            elif type == 'manual':
                slice_list[i][j] = denoising(slice_list[i][j], window_size=kwargs.get('window_size', 0))
    return slice_list
            

def create_connected_component_slices(image, color, **kwargs):
    original_image, slice_list, size, slice_border = slice_image(image)
    
    if not color:
        original_image, slice_list = convert_to_black_white(original_image, slice_list)
        if kwargs.get('denoise_type', 'none') == 'auto':
            denoise_list(slice_list, 'auto')
        elif kwargs.get('denoise_type', 'none') == 'manual':
            denoise_list(slice_list, 'manual', window_size=kwargs.get('window_size', 0))                
    
    width, height = size

    image = copy.deepcopy(original_image)

    boolean_list = []
    result_image_list = []
    for i, row in enumerate(slice_list):
        
        row_boolean_list = []
        row_result_image_list = []

        for j, slice_element in enumerate(row):
            if is_blank(slice_element, color):
                row_boolean_list.append(False)
                
                x1 = slice_border[i][j]['left']
                x2 = slice_border[i][j]['right']
                y1 = slice_border[i][j]['up'] 
                y2 = slice_border[i][j]['down']
            
                result_image = slice_element

            else:
                row_boolean_list.append(True)
                x1, x2, y1, y2 = get_connected_component_corners(slice_element, color) 
                
                connected_component_img = [row[x1:x2+1] for row in slice_element][y1:y2+1]                
                result_image, x_border_size, y_border_size, not_enough = append_white(connected_component_img, color)
                
                x1 += slice_border[i][j]['left']
                x2 += slice_border[i][j]['left']
                y1 += slice_border[i][j]['up'] 
                y2 += slice_border[i][j]['up']
                
                x1 -= x_border_size
                x2 += x_border_size
                y1 -= y_border_size
                y2 += y_border_size
                if not_enough == 'length':
                    x2 += 1
                elif not_enough == 'width':
                    y2 += 1 

            if not color:
                result_image = adjust_thick(result_image, kwargs.get('thickness', 1))

            cv.rectangle(image, (x1-1, y1-1), (x2+1, y2+1), (0, 0, 255), 1)
            image = insert_into_image(image, result_image, x1, y1, color)
            
            row_result_image_list.append(result_image)

        boolean_list.append(row_boolean_list)
        result_image_list.append(row_result_image_list)
    
    return image, result_image_list, boolean_list

def create_box_slices(image, color, **kwargs):
    original_image, slice_list, size, slice_border = slice_image(image)
    
    if not color:
        original_image, slice_list = convert_to_black_white(original_image, slice_list)
        if kwargs.get('denoise_type', 'none') == 'auto':
            denoise_list(slice_list, 'auto')
        elif kwargs.get('denoise_type', 'none') == 'manual':
            denoise_list(slice_list, 'manual', window_size=kwargs.get('window_size', 0))                
    
    width, height = size

    image = copy.deepcopy(original_image)

    boolean_list = []
    result_image_list = []
    for i, row in enumerate(slice_list):
        
        row_boolean_list = []
        row_result_image_list = []

        for j, slice_element in enumerate(row):
            
            if is_blank(slice_element, color):
                row_boolean_list.append(False)
            else:
                row_boolean_list.append(True)
            
            x1 = slice_border[i][j]['left']
            x2 = slice_border[i][j]['right']
            y1 = slice_border[i][j]['up'] 
            y2 = slice_border[i][j]['down']
            
            result_image = slice_element
            
            if not color:
                result_image = adjust_thick(result_image, kwargs.get('thickness', 1))
            
            cv.rectangle(image, (x1-1, y1-1),  (x2+1, y2+1), (0, 0, 255), 1)
            image = insert_into_image(image, result_image, x1, y1, color)
            row_result_image_list.append(result_image)

        boolean_list.append(row_boolean_list)
        result_image_list.append(row_result_image_list)
    
    return image, result_image_list, boolean_list

def save_image_cv(image, path):
    cv.imwrite(path, np.array(image))

def denoising(img, **kwargs):   
    #consume opencv image without window size
    #eturn denoised opencv image

    # b,g,r = cv.split(img)           # get b,g,r
    # rgb_img = cv.merge([r,g,b])     # switch it to rgb

    # Denoising
    dst = cv.fastNlMeansDenoising(img,None,10,7,kwargs.get('window_size', 21))
    return dst

def adjust_thick(img,thickness):
    result = img
    if (thickness>0):
        kernel = np.ones((thickness),np.uint8)
        result = cv.erode(img,kernel,iterations=1)
    elif (thickness<0):
        kernel = np.ones((-1*thickness),np.uint8)
        result = cv.dilate(img,kernel,iterations=1)
    return result
def split_by_box(path):
    image = cv.imread(path)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    thresh = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,57,5)
    cnts = cv.findContours(thresh.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts_sorted = sorted(cnts, key = cv.contourArea, reverse = True)
    squares = []
    for c in cnts:
        peri = cv.arcLength(c,True)
        approx = cv.approxPolyDP(c, 0.01 * peri, True)
        if (len(approx) == 4 and  cv.contourArea(approx)>cv.contourArea(cnts_sorted[7])-0.5*cv.contourArea(cnts_sorted[7]) and cv.contourArea(approx)<cv.contourArea(cnts_sorted[7])+0.5*cv.contourArea(cnts[7]) ):
            squares.append(approx)
    sorted_square = sort_contours(squares,"top-to-bottom")
    clasified = [sorted_square[i * 14:(i + 1) * 14] for i in range((len(sorted_square) + 14 - 1) // 14 )]
    bbox = []
    for c in clasified:
        temp = []
        for el in sort_contours(c,"left-to-right"):
            x = []
            y = []
            for point in el:
                x.append(point[0][0])
                y.append(point[0][1])
            left = min(x)
            top = min(y)
            right = max(x)
            bottom = max(y)
            temp.append((left+3,top+3,right-3,bottom-3))
        bbox.append(temp)
    return bbox

def sort_contours(cnts, method="left-to-right"):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0
	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True
	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1
	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
	# return the list of sorted contours and bounding boxes
	return cnts
