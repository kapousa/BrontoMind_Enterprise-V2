# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, request

from app import login_manager
from app.src.backend.directories.ProjectsDirector import ProjectsDirector
from app.src.backend.modules.projects import blueprint


## projects

@blueprint.route('/add', methods=['POST'])
def add_project():
    projects_director = ProjectsDirector()
    return projects_director.create_project(request)


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
