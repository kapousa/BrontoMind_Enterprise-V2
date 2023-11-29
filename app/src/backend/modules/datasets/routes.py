# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os

from flask import render_template, request, send_file, session
from flask_login import login_required

from app import login_manager
from app.src.backend.constants.BM_CONSTANTS import download_my_datasets, my_datasets
from app.src.backend.controllers.datasets.DatasetsController import DatasetsController
from app.src.backend.directories.datasets.DatasetsDirector import DatasetsDirector
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.modules.datasets import blueprint
from run import app

## datasets
app.config['DOWNLOAD_DATASETS_PATH'] = download_my_datasets
datasets_directory = DatasetsDirector()

@blueprint.route('/view')
@login_required
def view_datasets():
    return datasets_directory.view_datasets()

@blueprint.route('/datasource')
@login_required
def select_datasource():
    return render_template('applications/pages/mydatasets/datasource.html', segment='datasets')


@blueprint.route('/connecttods', methods=['POST'])
@login_required
def connectds():
    return datasets_directory.create_connection(request)

@blueprint.route('/savedataset', methods=['POST'])
@login_required
def save_dataset():
    return datasets_directory.save_dataset(request)
@blueprint.route('/<dataset_id>/downloaddataset')
@login_required
def download_mydataset(dataset_id):
    user_dataset = ModelMyDatasets.query.with_entities(ModelMyDatasets.name).filter_by(id=dataset_id).first()
    path = os.path.join(f"{download_my_datasets}{session['logger']}/{user_dataset.name}")
    return send_file(path, as_attachment=True)


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
