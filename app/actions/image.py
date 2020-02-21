import flask
import os
from datetime import datetime
from werkzeug.utils import secure_filename

def saveImage(image):
    current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
    filename = secure_filename(current_time)

    path = os.path.join("images/", filename + ".jpg")
    image.save(path)