# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os

from flask import render_template, request, send_file, session
from flask_login import login_required

from app import login_manager
from app.src.backend.constants.BM_CONSTANTS import download_my_datasets, temp_html_image_path
from app.src.backend.directories.datasets.DatasetsDirector import DatasetsDirector
from app.src.backend.directories.datasets.chat.ChatDirector import ChatDirector
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.modules.datasets import blueprint


## datasets
datasets_directory = DatasetsDirector()

@blueprint.route('/view')
@login_required
def view_datasets():
    return datasets_directory.view_datasets()

@blueprint.route('/<dataset_id>/<type>/createmodel')
@login_required
def create_model_from_datasets(dataset_id, type):
    return datasets_directory.set_model_goal(dataset_id, type)

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

@blueprint.route('/<dataset_id>/startchat')
@login_required
def start_chat(dataset_id):
    chat_director = ChatDirector()
    return chat_director.start_chat(dataset_id)

@blueprint.route('/<dataset_id>/reponsechat', methods=['POST'])
@login_required
def response_chat(dataset_id):
    chat_director = ChatDirector()
    return chat_director.chat_reponse(dataset_id)

@blueprint.route('/get_image/<image_name>')
@login_required
def get_image(image_name):
    # Generate dynamic image path
    image_path = os.path.join(temp_html_image_path, image_name)

    # Display the image using send_file
    return send_file(image_path, mimetype='image/png')


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
