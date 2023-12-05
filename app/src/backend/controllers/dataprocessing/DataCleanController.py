import logging
import os
import shutil

import pandas as pd
from flask import abort

from app.src.backend.controllers.dataprocessing.CleanDataEngine import CleanDataEngine
from app.src.backend.utiles.CVSReader import get_file_name_with_ext
from app.src.backend.constants.DATAPROCESSING_CONSTANTS import modified_files_temp_path


class DataCleanController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def drafting_clean_request(self, required_changes, file_path):
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower()
            data_columns = df.columns
            data_columns = [x for x in data_columns]

            clean_data_engine = CleanDataEngine()
            modified_data = clean_data_engine.applychanges(df, required_changes)

            # Copy original file to temp folder
            file_name = get_file_name_with_ext(file_path)
            destination_path = os.path.join(modified_files_temp_path)
            shutil.copy(file_path, destination_path)

            # Write the updated DataFrame back to the CSV file
            modified_data.to_csv(file_path, index=False)

            sample_data = modified_data.iloc[:10]

            return sample_data
        except Exception as e:
            logging.exception(e)
            print(e)
            abort(500, description=e)
