import logging

import numpy
from flask import render_template, session, abort
from app.src.backend.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path
from app.src.backend.controllers.datasets.DatasetsController import DatasetsController
from app.src.backend.controllers.projects.ProjectsController import ProjectsController
from app.src.backend.directories.BaseDirector import BaseDirector


class DatasetsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def create_connection(self, request):
        ds_id = request.form.get('ds_source')
        session['ds_id'] = ds_id
        return render_template('applications/pages/mydatasets/connecttods.html', ds_id=ds_id, segment='datasets')

    def save_data_set(self, request):
        try:
            f = request.files.getlist('filename[]')
            datasets_controller = DatasetsController()
            model = datasets_controller.save_tables_dateset(session['logger'], session['ds_id'], f)
            session.pop('ds_id')

            return render_template('applications/pages/mydatasets/mydatasets.html', segment='datasets')

        except Exception as e:
            logging.error(e)
            abort(500)