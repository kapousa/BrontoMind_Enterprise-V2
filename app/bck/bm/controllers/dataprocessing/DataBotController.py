import logging

import pandas as pd
from flask import abort

from app.bck.bm.controllers.dataprocessing.DataBotControllerHelper import DataBotControllerHelper
from app.bck.bm.core.engine.processors.WordProcessor import WordProcessor


class DataBotController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def drafting_bot_request(self, user_text, file_path):
        try:
            df = pd.read_csv(file_path)
            df = df.iloc[:10]
            df.columns = df.columns.str.lower()
            data_columns = df.columns
            data_columns = [x for x in data_columns]

            wordprocessor = WordProcessor()
            databotcontrollerhelper = DataBotControllerHelper()

            required_changes = wordprocessor.get_orders_list(user_text, data_columns)
            modified_data = databotcontrollerhelper.apply_bot_changes(required_changes, df)

            #dataBotcontrollerhelper = DataBotControllerHelper()
            #required_changes, modified_data = dataBotcontrollerhelper.update_csv_with_text(df, user_text)

            return required_changes, modified_data
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def apply_bot_request(self, file_path, required_changes):
        try:
            databotcontrollerhelper = DataBotControllerHelper()

            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower()
            modified_data = databotcontrollerhelper.apply_bot_changes(required_changes, df)
            modified_data.to_csv(file_path)
            modified_data = modified_data.iloc[:10]

            return required_changes, modified_data
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)
