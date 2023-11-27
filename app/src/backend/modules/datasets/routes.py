# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, request
from flask_login import login_required

from app import login_manager
from app.src.backend.modules.datasets import blueprint


## projects

@blueprint.route('/view')
@login_required
def view_datasets():
    return render_template('applications/pages/mydatasets/mydatasets.html', segment='datasets')

@blueprint.route('/datasource')
@login_required
def select_datasource():
    return render_template('applications/pages/mydatasets/datasource.html', segment='datasets')



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
