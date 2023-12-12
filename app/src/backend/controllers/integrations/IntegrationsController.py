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
                    "description": user_integration.description,
                    "connection_string": user_integration.connection_string
                }
                integrations.append(integration_info)

            return integrations

        except Exception as e:
            logging.error(e)
            print(e)
            abort(500)
