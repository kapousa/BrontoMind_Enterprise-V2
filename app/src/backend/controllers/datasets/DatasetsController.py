import logging
import os
from pathlib import Path

import chardet
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

            number_of_exsiting_files = Helper.count_files_with_string(os.path.dirname(f"{my_datasets}{user_id}/"),
                                                                      secure_filename(fname))
            fname = fname if number_of_exsiting_files == 0 else f"{number_of_exsiting_files}_{fname}"
            filePath = os.path.join(f"{my_datasets}{user_id}/", secure_filename(fname))

            f[0].save(filePath)

            # Get dataset file information
            try:
                detected = chardet.detect(Path(filePath).read_bytes())
                encoding = detected.get("encoding")
                assert encoding, "Unable to detect encoding, is it a binary file?"
                file_size_bytes = os.path.getsize(filePath)
                file_size_kb = round(file_size_bytes / 1024.0, 2)
                file_size_mb = round(file_size_kb / 1024.0, 2)
                df = pd.read_csv(filePath, encoding=encoding)
                num_rows, num_columns = df.shape
            except UnicodeDecodeError as ude:
                print(f"Unable to detect encoding {fname}, is it a binary file?")
                logging.error(ude)
                num_rows = 'Unable to read'
                num_columns = 'Unable to read'


            # Add file record to the DB
            now = datetime.now()
            modelmodel = {'id': Helper.generate_id(),
                          'name': fname,
                          'type': dataset_type,
                          'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'created_by': user_id,
                          'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'updated_by': user_id,
                          'file_size_mb': file_size_mb,
                          'num_rows': num_rows,
                          'num_columns': num_columns,
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
            user_datasets = ModelMyDatasets.query.filter_by(user_id=user_id).all()
            datasets_info = []
            for user_dataset in user_datasets:
                dataset_info = {
                    "id": user_dataset.id,
                    "name": user_dataset.name,
                    "type": user_dataset.type,
                    "num_columns": user_dataset.num_columns,
                    "num_rows": user_dataset.num_rows,
                    "size": user_dataset.file_size_mb
                }
                datasets_info.append(dataset_info)

            return datasets_info

        except Exception as e:
            logging.error(e)
            abort(500)
