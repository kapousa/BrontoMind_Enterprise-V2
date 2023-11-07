# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import logging
import os

from flask import abort, request, session, send_file
from flask_login import login_required

from app.bck.bm.utiles.CVSReader import get_file_name_with_ext
from app.constants.BM_CONSTANTS import df_location, data_files_folder
from app.modules.base.app_routes.directors.dataprocessing.DataProcessingDirector import DataProcessingDirector
from app.modules.dataprocessing import blueprint

## Data Processing

databotdirector = DataProcessingDirector()

@blueprint.route('/datapreprationbot', methods=['GET', 'POST'])
@login_required
def datapreprationbot():
    try:
        return databotdirector.data_prepration_bot(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/builddataset', methods=['GET', 'POST'])
@login_required
def build_dataset():
    try:
        return databotdirector.build_data_sheet(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/previewchanges', methods=['GET', 'POST'])
@login_required
def previewchanges():
    try:
        return databotdirector.preview_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/applychanges', methods=['GET', 'POST'])
@login_required
def applychanges():
    try:
        return databotdirector.apply_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/downloadmodifiedfile', methods=['GET', 'POST'])
@login_required
def downloadmodifiedfile():
    try:
        return databotdirector.download_modifiedfile(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/cancelmodifications', methods=['GET', 'POST'])
@login_required
def cancelmodifications():
    try:
        return databotdirector.cancel_modifiedfile(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/previewchatchanges', methods=['GET', 'POST'])
@login_required
def previewchatchanges():
    try:
        return databotdirector.preview_chat_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/applychatresponse', methods=['GET', 'POST'])
@login_required
def applychatresponse():
    try:
        return databotdirector.apply_chat_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/previewcleanchanges', methods=['GET', 'POST'])
@login_required
def previewcleanchanges():
    try:
        return databotdirector.preview_clean_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/applycleanresponse', methods=['GET', 'POST'])
@login_required
def applycleanresponse():
    try:
        return databotdirector.apply_clean_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/matchfields', methods=['GET', 'POST'])
@login_required
def matchfields():
    try:
        return databotdirector.match_merging_fields(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/previewmergechanges', methods=['GET', 'POST'])
@login_required
def previewmergechanges():
    try:
        return databotdirector.preview_merge_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/rematch', methods=['GET', 'POST'])
@login_required
def rematch():
    try:
        return databotdirector.rematch()
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/applymergeresponse', methods=['GET', 'POST'])
@login_required
def applymergeresponse():
    try:
        return databotdirector.apply_merge_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/cancelchanges', methods=['GET', 'POST'])
@login_required
def cancelchanges():
    try:
        return databotdirector.cancel_changes(request)
    except Exception as e:
        logging.error(e)
        abort(500, e)

@blueprint.route('/downloaddata', methods=['GET', 'POST'])
@login_required
def downloaddata():
    f = get_file_name_with_ext(session['filepath'])
    path = os.path.join(data_files_folder, f)
    return send_file(path, as_attachment=True)