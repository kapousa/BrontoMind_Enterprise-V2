import logging
import os.path

import numpy
from flask import render_template, session, abort, send_file, redirect, url_for
from app.src.backend.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path, my_datasets, \
    download_my_datasets
from app.src.backend.controllers.datasets.DatasetsController import DatasetsController
from app.src.backend.controllers.projects.ProjectsController import ProjectsController
from app.src.backend.controllers.reports.ReportsController import ReportsController
from app.src.backend.directories.BaseDirector import BaseDirector
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets


class ReportsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def full_analyze(self, dataset_id):
        reports_controller = ReportsController()
        dataset_id, dataset, descriptive_report = reports_controller.get_full_analysis(
            session['logger'], dataset_id)
        return render_template('applications/pages/reports/quickreport.html', dataset_id=dataset_id, dataset=dataset,
                               descriptive_report=descriptive_report,
                               segment='datasets')

    def show_state_page(self, dataset_id):
        return render_template(f"applications/reports/{session['logger']}/{dataset_id}/stats.html")
