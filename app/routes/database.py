import flask
from flask import request, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

def create_database_blueprint(app):
    database_blueprint = Blueprint('database', __name__)
    db = SQLAlchemy(app)
    ma = Marshmallow(app)

    class Project(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        project_name = db.Column(db.String(256), unique=True)
        pixels = db.Column(db.Integer)

        def __init__(self, project_name, pixels):
            self.project_name = project_name
            self.pixels = pixels

    class ProjectSchema(ma.Schema):
        class Meta:
            # Fields to expose
            fields = ('id','project_name', 'pixels')

    project_schema = ProjectSchema()
    projects_schema = ProjectSchema(many=True)

    # endpoint to add new project
    @database_blueprint.route("/project", methods=["POST"])
    def add_project():
        project_name = request.json['project_name']
        pixels = request.json['pixels']
        
        new_project = Project(project_name, pixels)

        db.session.add(new_project)
        db.session.commit()

        return jsonify(success = True)

    # endpoint to show all projects
    @database_blueprint.route("/project", methods=["GET"])
    def get_project():
        all_project = Project.query.all()
        result = projects_schema.dump(all_project)
        
        return jsonify(result)

    # endpoint to get project detail by id
    @database_blueprint.route("/project/<id>", methods=["GET"])
    def project_detail(id):
        project = Project.query.get(id)
        
        return project_schema.jsonify(project)

    # endpoint to update project by id
    @database_blueprint.route("/project/<id>", methods=["PUT"])
    def project_update(id):
        project = Project.query.get(id)
        project_name = request.json['project_name']
        pixels = request.json['pixels']

        project.project_name = project_name
        project.pixels = pixels
        db.session.commit()
        
        return project_schema.jsonify(project)

    # endpoint to delete project
    @database_blueprint.route("/project/<id>", methods=["DELETE"])
    def project_delete(id):
        project = Project.query.get(id)
        db.session.delete(project)
        db.session.commit()

        return project_schema.jsonify(project)
    
    app.register_blueprint(database_blueprint, url_prefix='/database')