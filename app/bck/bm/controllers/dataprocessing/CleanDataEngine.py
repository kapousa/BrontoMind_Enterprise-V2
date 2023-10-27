import pandas as pd


class CleanDataEngine:
    df = None
    functions_list = ['_standardizedatacolumns', '_removeunexpectednulls']

    def __init__(self):
        """ Constructor for this class. """
        self.df = None

    def applychanges(self, dataset, required_changes):
        self.df = dataset

        for index in required_changes:
            if hasattr(self, self.functions_list[index]) and callable(getattr(self, self.functions_list[index])):
                func = getattr(self, self.functions_list[index])
                func()
            else:
                print("Function not found or not callable")

        return self.df

    def _standardizedatacolumns(self):
        """ Convert all date columns to ISO 8601 standard format. """

        for col in self.df.select_dtypes(include='datetime64'):
            self.df[col] = self.df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

        return self.df

    def _removeunexpectednulls(self):
        """ Remove rows with null values for columns that are at least 99% filled in. """

        # Calculate the percentage of missing values in each column
        null_percentage = self.df.isnull().mean() * 100

        # Set the threshold (99% filled)
        threshold = 1

        # Get the column names that have less than 'threshold' percentage of missing data
        columns_to_keep = null_percentage[null_percentage <= threshold].index

        # Remove rows with null values in the selected columns
        return self.df.dropna(subset=columns_to_keep)
