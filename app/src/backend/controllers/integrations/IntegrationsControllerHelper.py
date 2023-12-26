import itertools
import json
import logging
import inspect
import os
from pathlib import Path

import chardet
import pandas as pd
import requests
from flask import abort, session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT, my_datasets
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.models.ModelDatasets import ModelDatasets
from app.src.backend.models.ModelIntegrationDetails import ModelIntegrationDetails
from app.src.backend.models.ModelIntegrations import ModelIntegrations
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.modules.base.routes import root_path
from app.src.backend.utiles.Helper import Helper

from datetime import datetime


class IntegrationsControllerHelper:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals

        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    @staticmethod
    def save_integration(connection_type, **connection_info):
        ''' Save the integration details '''

        try:
            # Save basic information of the integration
            integration_id = Helper.generate_id()
            connections_basic_info = {
                "id": integration_id,
                "name": connection_info.get('integration_name'),
                "description": connection_info.get('integration_description'),
                "type": int(connection_type),
                "user_id": session['logger']
            }
            integration_model = ModelIntegrations(**connections_basic_info)
            db.session.commit()
            db.session.add(integration_model)
            db.session.commit()

            # Save connetions details
            for k, v in connection_info.items():
                connection_details = {}
                if (k == "integration_name" or k == "integration_description"):
                    continue
                connection_details['param_name'] = k
                connection_details['param_value'] = v
                connection_details['integration_id'] = integration_id
                integration_details_model = ModelIntegrationDetails(**connection_details)
                db.session.commit()
                db.session.add(integration_details_model)
                db.session.commit()

            return integration_id

        except Exception as e:
            logging.error(e)
            print(e)
            db.session.rollback()
            db.session.close()
            return None

    @staticmethod
    def fetch_api_results(**connection_info):
        try:
            api_url = connection_info['api_url']
            request_type = connection_info['request_type']
            headers = connection_info['headers'] if connection_info['headers'] != '' else None
            root_node = connection_info['root_node'] if connection_info['root_node'] != '' else None
            request_parameters = connection_info['request_parameters']
            api_response = requests.get(url=api_url,
                                        json=request_parameters,
                                        headers=headers) if request_type == 'type_get' else requests.post(
                url=api_url, json=request_parameters, headers=headers)

            if api_response.status_code != 200:
                raise Exception("Error calling the API.")
                return None

            # Create json file
            json_response = json.loads(api_response.text)
            df = pd.json_normalize(json_response) if root_node == None else pd.json_normalize(json_response[root_node])
            df = pd.DataFrame(df)

            return df

        except (Exception, JSONDecodeError) as e:
            frame = inspect.currentframe()
            method_name = frame.f_code.co_name
            err_msg = f"Error when call {method_name} method: {e}"
            print(err_msg)
            logging.error(err_msg)

            return None

    @staticmethod
    def export_to_mydataset(integration_id, integration_name, df, dataframe_source, user_id, add=True):
        ''' Export data fetched by integration connection to MyDataset'''
        try:
            fname = f"{integration_name}.csv"
            filePath = os.path.join(f"{my_datasets}{user_id}/", fname)
            df.to_csv(filePath)

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

            now = datetime.now()
            if add:
                # Add file record to the DB
                modelmodel = {'id': Helper.generate_id(),
                              'name': fname,
                              'type': dataframe_source,
                              'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                              'created_by': user_id,
                              'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                              'updated_by': user_id,
                              'file_size_mb': file_size_mb,
                              'num_rows': num_rows,
                              'num_columns': num_columns,
                              'user_id': user_id,
                              'integration_id': integration_id}

                model_model = ModelMyDatasets(**modelmodel)
                db.session.commit()
                # Add new profile
                db.session.add(model_model)
                db.session.commit()
            else:
                model_model = ModelMyDatasets.query.filter_by(integration_id=integration_id).first()
                model_model.updated_by = user_id
                model_model.updated_on = now.strftime("%d/%m/%Y %H:%M:%S")
                model_model.file_size_mb = file_size_mb
                model_model.num_rows = num_rows
                model_model.num_columns = num_columns
                db.session.commit()

            return model_model

        except Exception as e:
            db.session.rollback()
            frame = inspect.currentframe()
            method_name = frame.f_code.co_name
            err_msg = f"Error when call {method_name} method: {e}"
            print(err_msg)
            logging.error(err_msg)

            return None
