import logging
import os

from flask import abort
from werkzeug.utils import secure_filename

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT, my_datasets
from app.src.backend.models.ModelDatasets import ModelDatasets
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.utiles.Helper import Helper

from datetime import datetime


class DatasetsController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def save_tables_dateset(self, user_id, dataset_type, data_files):
        ''' Saves datasets of type tables (csv, excel sheets, ....)'''
        try:
            # Save the file
            f = data_files
            fname = secure_filename(f[0].filename)
            filePath = os.path.join(f"{my_datasets}{user_id}/", secure_filename(fname))
            f[0].save(filePath)

            # Add file record to the DB
            now = datetime.now()
            modelmodel = {'id': Helper.generate_id(),
                          'name': fname,
                          'type': dataset_type,
                          'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'created_by': user_id,
                          'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'updated_by': user_id,
                          'user_id': user_id}

            model_model = ModelMyDatasets(**modelmodel)
            db.session.commit()
            # Add new profile
            db.session.add(model_model)
            db.session.commit()

            return modelmodel


        except Exception as e:
            db.session.rollback()
            logging.error(e)
            abort(500)
