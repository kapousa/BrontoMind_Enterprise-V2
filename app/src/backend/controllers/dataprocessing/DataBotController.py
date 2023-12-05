import logging
import os
import shutil

import pandas as pd
from flask import abort

from app.src.backend.controllers.dataprocessing.DataBotControllerHelper import DataBotControllerHelper
from app.src.backend.core.engine.processors.WordProcessor import WordProcessor
from app.src.backend.utiles.CVSReader import get_file_name_with_ext
from app.src.backend.constants.DATAPROCESSING_CONSTANTS import modified_files_temp_path


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

            # Copy original file to temp folder
            file_name = get_file_name_with_ext(file_path)
            destination_path = os.path.join(modified_files_temp_path)
            shutil.copy(file_path, destination_path)

            # Write the updated DataFrame back to the CSV file
            modified_data.to_csv(file_path, index=False)

            #dataBotcontrollerhelper = DataBotControllerHelper()
            #required_changes, modified_data = dataBotcontrollerhelper.update_csv_with_text(df, user_text)

            return required_changes, modified_data
        except Exception as e:
            logging.exception(e)
            print(e)
            abort(500, description=e)

    def apply_bot_request(self, file_path, required_changes):
        try:
            databotcontrollerhelper = DataBotControllerHelper()

            df = pd.read_csv(file_path)
            df_orginal = df
            df_orginal.to_csv("{}{}".format(file_path, "orgi"))     # Save original data
            df.columns = df.columns.str.lower()
            modified_data = databotcontrollerhelper.apply_bot_changes(required_changes, df)
            modified_data.to_csv(file_path)
            modified_data = modified_data.iloc[:10]

            return required_changes, modified_data
        except Exception as e:
            logging.exception(e)
            print(e)
            abort(500, description=e)
