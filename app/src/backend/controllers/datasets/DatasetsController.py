import logging
import os

import pandas as pd
from flask import abort
from werkzeug.utils import secure_filename

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT, my_datasets
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.models.ModelDatasets import ModelDatasets
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.modules.base.routes import root_path
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

    def get_datasets(self, user_id):
        ''' Return all datasets of a user '''

        try:
            user_datasets = ModelMyDatasets.query.with_entities(ModelMyDatasets.id, ModelMyDatasets.name,
                                                                ModelMyDatasets.type).filter_by(user_id=user_id).all()
            datasets_info = []
            for user_dataset in user_datasets:
                dataset_file_path = f"{my_datasets}{user_id}/{user_dataset.name}"
                df = pd.read_csv(dataset_file_path)
                file_size_bytes = os.path.getsize(dataset_file_path)
                num_rows, num_columns = df.shape
                file_size_kb = file_size_bytes / 1024.0
                file_size_mb = round(file_size_kb / 1024.0, 2)

                dataset_info = {
                    "id": user_dataset.id,
                    "name": user_dataset.name,
                    "type": user_dataset.type,
                    "num_columns": num_columns,
                    "num_rows": num_rows,
                    "size": file_size_mb
                }
                datasets_info.append(dataset_info)

            return datasets_info
        except Exception as e:
            logging.error(e)
            abort(500)
