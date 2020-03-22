import flask
from flask import Flask, jsonify
from datetime import datetime
import os

import config
from routes.image import image_blueprint
from routes.database import create_database_blueprint

app = Flask(__name__)

app.register_blueprint(image_blueprint, url_prefix='/image')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/db.sqlite')
create_database_blueprint(app)



@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')

    return response

@app.route('/', methods=['GET', 'POST'])
def get():
    current_time = datetime.now()

    return jsonify({"time": current_time })

app.run(port = config.PORT)

