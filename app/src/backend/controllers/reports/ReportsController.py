import logging

import pandas as pd
from flask import abort

from app.src.backend.constants.BM_CONSTANTS import my_datasets
from app.src.backend.controllers.reports.ReportsControllerHelper import ReportsControllerHelper
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets


class ReportsController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def get_full_analysis(self, user_id, dataset_id, report_type=1):
        try:
            mydataset = ModelMyDatasets.query.with_entities(ModelMyDatasets.name).filter_by(id=dataset_id, user_id=user_id).first()
            file_path = f"{my_datasets}{user_id}/{mydataset.name}"
            df = pd.read_csv(file_path)
            #html_file_locations = ReportsControllerHelper.generatecharts(user_id, dataset_id, df)
            reports_controller_helper = ReportsControllerHelper()
            descriptive_report = reports_controller_helper.generateanalysisreport(user_id, dataset_id, df, report_type)

            return dataset_id, mydataset.name, descriptive_report

        except Exception as e:
            print(e)
            logging.error(e)
            abort(500)
