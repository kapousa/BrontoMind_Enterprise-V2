import os
import shutil

import pandas as pd
from pandas.errors import MergeError

from app.src.backend.constants.DATAPROCESSING_CONSTANTS import modified_files_temp_path


class DataMergeController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def drafting_merge_request(self, original_file_path, secondary_file_path, original_matching_columns,
                               secondary_matching_columns, merge_type='left'):
        """ Merge all rows from the original dataset with mathing rows from the secondary dataset. """
        try:
            original_file = original_file_path
            secondary_file = secondary_file_path
            original_dataset = pd.read_csv(original_file)
            secondary_dataset = pd.read_csv(secondary_file)

            # Copy original file to temp folder
            destination_path = os.path.join(modified_files_temp_path)
            shutil.copy(original_file, destination_path)

            # Define a dictionary to map old column names to new column names
            column_mapping = {}
            for i in range(len(original_matching_columns)):
                column_mapping[secondary_matching_columns[i]] = original_matching_columns[i]

            secondary_dataset.rename(columns=column_mapping, inplace=True)
            merged_df = original_dataset.merge(secondary_dataset, on=original_matching_columns, how=merge_type)

            merged_file = "{}s".format(secondary_file)
            merged_df.to_csv(original_file, index=False)
            sample_data = merged_df.iloc[:10]

            return sample_data

        except (MergeError, ValueError, KeyError, TypeError, MemoryError) as e:

            print(f"An exception occurred: {e}")

            # Handle the exception or take appropriate action
            return "You are attempting to merge columns of different types; if you continue, we will concatenate the matched values."
