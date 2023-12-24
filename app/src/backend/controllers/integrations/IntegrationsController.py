import inspect
import itertools
import logging
import os
from pathlib import Path

import chardet
import pandas as pd
from flask import abort, session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT, my_datasets
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.controllers.integrations.IntegrationsControllerHelper import IntegrationsControllerHelper
from app.src.backend.models.ModelDatasets import ModelDatasets
from app.src.backend.models.ModelIntegrationDetails import ModelIntegrationDetails
from app.src.backend.models.ModelIntegrations import ModelIntegrations
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.modules.base.routes import root_path
from app.src.backend.utiles.Helper import Helper

from datetime import datetime


class IntegrationsController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def get_integrations(self, user_id):
        ''' Return all datasets of a user '''

        try:
            user_integrations = ModelIntegrations.query.filter_by(user_id=user_id).all()
            integrations = []
            for user_integration in user_integrations:
                integration_info = {
                    "id": user_integration.id,
                    "name": user_integration.name,
                    "type": user_integration.type,
                    "type_name": Helper.get_lookup_value(user_integration.type),
                    "description": user_integration.description,
                    "connection_string": user_integration.connection_string
                }
                integrations.append(integration_info)

            return integrations

        except Exception as e:
            logging.error(e)
            print(e)
            abort(500)

    def create_integration(self, connection_type, **connection_info):
        ''' Create the integration '''
        try:
            # Fetch data
            df = IntegrationsControllerHelper.fetch_api_results(**connection_info)

            if df is None:
                return False

            # Save information of the integration
            saved_integration_id = IntegrationsControllerHelper.save_integration(connection_type, **connection_info)

            # Export data to my datasets
            export_to_mydataset = IntegrationsControllerHelper.export_to_mydataset(saved_integration_id,
                                                                                   connection_info.get(
                                                                                       'integration_name'), df,
                                                                                   connection_type, session['logger'])

            return True

        except Exception as e:
            frame = inspect.currentframe()
            method_name = frame.f_code.co_name
            err_msg = f"Error when call {method_name} method: {e}"
            print(err_msg)
            logging.error(err_msg)

            return False
