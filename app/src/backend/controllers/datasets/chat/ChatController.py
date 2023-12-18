import logging
import os
from pathlib import Path

import chardet
import numpy as np
import pandas as pd
from flask import abort
from werkzeug.utils import secure_filename

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT, my_datasets
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.controllers.datasets.chat.ChatControllerHelper import ChatControllerHelper
from app.src.backend.models.ModelDatasets import ModelDatasets
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.modules.base.routes import root_path
from app.src.backend.utiles.Helper import Helper

from datetime import datetime


class ChatController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def start_chat(self, user_id, dataset_id):
        ''' Response to chat prompt '''
        try:
            my_datasets = ModelMyDatasets.query.filter_by(user_id=user_id, id=dataset_id).first()
            return my_datasets.name
        except Exception as e:
            print(e)
            logging.error(e)
            abort(500)

    def get_response(self, user_id, dataset_id, user_input):
        ''' Response to chat prompt '''
        try:
            my_dataset = ModelMyDatasets.query.filter_by(user_id=user_id, id=dataset_id).first()
            df = pd.read_csv(f"{my_datasets}/{user_id}/{my_dataset.name}")

            chat_controller_helper = ChatControllerHelper()
            return chat_controller_helper.generate_response(df, user_input)

        except Exception as e:
            print(e)
            logging.error(e)
            return []
