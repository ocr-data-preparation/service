import flask
from flask import request, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import cross_origin
import os

def create_project_blueprint(app):
    project_blueprint = Blueprint('project', __name__)
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
    @project_blueprint.route("/", methods=["POST"])
    @cross_origin()
    def add_project():
        project_name = request.json['project_name']
        pixels = request.json['pixels']
        
        new_project = Project(project_name, pixels)

        db.session.add(new_project)
        db.session.commit()
        project = Project.query.filter(Project.project_name == project_name).first()
        return project_schema.jsonify(project)

    # endpoint to show all projects
    @project_blueprint.route("/", methods=["GET"])
    @cross_origin()
    def get_project():
        all_project = Project.query.all()
        result = projects_schema.dump(all_project)
        
        return jsonify(result)

    # endpoint to get project detail by id
    @project_blueprint.route("/<id>", methods=["GET"])
    @cross_origin()
    def project_detail(id):
        project = Project.query.get(id)
        
        return project_schema.jsonify(project)

    # endpoint to update project by id
    @project_blueprint.route("/<id>", methods=["PUT"])
    @cross_origin()
    def project_update(id):
        project = Project.query.get(id)
        project_name = request.json['project_name']
        pixels = request.json['pixels']

        project.project_name = project_name
        project.pixels = pixels
        db.session.commit()
        
        return project_schema.jsonify(project)

    # endpoint to delete project
    @project_blueprint.route("/<id>", methods=["DELETE"])
    @cross_origin()
    def project_delete(id):
        project = Project.query.get(id)
        db.session.delete(project)
        db.session.commit()

        return project_schema.jsonify(project)
    
    app.register_blueprint(project_blueprint, url_prefix='/project')