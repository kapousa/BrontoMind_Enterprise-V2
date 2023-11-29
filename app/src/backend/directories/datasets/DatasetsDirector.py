import logging
import os.path

import numpy
from flask import render_template, session, abort, send_file
from app.src.backend.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path, my_datasets, \
    download_my_datasets
from app.src.backend.controllers.datasets.DatasetsController import DatasetsController
from app.src.backend.controllers.projects.ProjectsController import ProjectsController
from app.src.backend.directories.BaseDirector import BaseDirector
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets


class DatasetsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def view_datasets(self):
        datasets_controller = DatasetsController()
        datasets = datasets_controller.get_datasets(session['logger'])
        return render_template('applications/pages/mydatasets/mydatasets.html', datasets=datasets, segment='datasets')

    def create_connection(self, request):
        ds_id = request.form.get('ds_source')
        session['ds_id'] = ds_id
        return render_template('applications/pages/mydatasets/connecttods.html', ds_id=ds_id, segment='datasets')

    def save_dataset(self, request):
        try:
            f = request.files.getlist('filename[]')
            datasets_controller = DatasetsController()
            model = datasets_controller.save_tables_dateset(session['logger'], session['ds_id'], f)
            session.pop('ds_id')

            datasets_controller = DatasetsController()
            datasets = datasets_controller.get_datasets(session['logger'])

            return render_template('applications/pages/mydatasets/mydatasets.html', datasets=datasets,
                                   segment='datasets')

        except Exception as e:
            logging.error(e)
            abort(500)


    def downlaoddataset(self, dataset_id):
        user_dataset = ModelMyDatasets.query.with_entities(ModelMyDatasets.name).filter_by(id=dataset_id).first()
        path = os.path.join(f"{download_my_datasets}{session['logger']}/{user_dataset.name}")
        return send_file(path, as_attachment=True)
