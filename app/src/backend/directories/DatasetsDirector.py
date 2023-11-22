import logging
from os import abort

from flask import render_template

from app.src.backend.constants.BM_CONSTANTS import downlaod_dataset_file_path
from app.src.backend.models.ModelDatasets import ModelDatasets


class DatasetsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    @staticmethod
    def view_all():
        try:
            model_datasets = ModelDatasets.query.order_by("file_name").all()

            # # Get a list of all files in the folder
            # files = os.listdir(datasets_files)
            #
            # # get the list of files
            # datasets_files_arr = []
            # for file_name in files:
            #     print(file_name)
            #
            #     # Read the CSV file
            #     data = pd.read_csv("{0}/{1}".format(datasets_files, file_name), nrows=5, usecols=[0,1,2])
            #
            #     # Convert the DataFrame to HTML
            #     #table_html = data.to_html()
            #     datasets_files_arr.append(data.to_html())

            # Render the HTML template with the CSV data
            return render_template('applications/pages/datasets/viewall.html', model_datasets=model_datasets, segment='datasets')

        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    @staticmethod
    def downlaod_datasets(id):
        model_datasets = ModelDatasets.query.filter_by(id=id).first()
        path = "{0}/{1}".format(downlaod_dataset_file_path, model_datasets.file_name)
        return path

