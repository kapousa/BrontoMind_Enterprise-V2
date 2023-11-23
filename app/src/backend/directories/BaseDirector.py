import logging
import os

import numpy
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import flask
from flask import render_template, session, redirect, url_for, abort
from werkzeug.utils import secure_filename

from app.src.backend.constants.BM_CONSTANTS import df_location
from app.src.backend.constants.BM_CONSTANTS import api_data_filename
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.utiles.db.datamanipulation.AdjustDataFrame import export_mysql_query_to_csv, \
    export_api_respose_to_csv
from app.src.backend.utiles.CVSReader import getcvsheader, get_file_name_with_ext
from app.src.backend.utiles.Helper import Helper


class BaseDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    @staticmethod
    def load_home(request):
        """ Load user's homepage"""
        basecontroller = BaseController()
        development_projects, production_projects, archive_projects = basecontroller.get_projects(session['logger'])
        development_projects_message = 'There is no any development projects' if len(development_projects) == 0 else ''
        production_projects_message = 'There is no any production projects' if len(production_projects) == 0 else ''
        archive_projects_message = 'There is no any archive projects' if len(archive_projects) == 0 else ''
        return render_template('applications/pages/projects.html', development_projects=development_projects,
                               production_projects=production_projects, archive_projects=archive_projects,
                               development_projects_message=development_projects_message,
                               production_projects_message=production_projects_message,
                               archive_projects_message=archive_projects_message,
                               segment='projects')

    @staticmethod
    def get_data_details(request):
        try:
            f = flask.request.files.getlist('filename[]')
            ds_source = session['ds_source']
            ds_goal = session['ds_goal']

            if len(f) > 0:  # not 'filepath' in session:
                f = flask.request.files.getlist('filename[]')
                model_id = Helper.generate_id()

                # file_Path = session['filePath'] if session['filePath'] is not None else f
                # file_Path = flask.request.form.get("filePath")
                # file_Path = session["filePath"]
                # filePath = file_Path
                number_of_files = len(f) if f != None else 0
                if number_of_files == 1:  # or file_Path != None:  # Check if there file sent to upload or already uploaded in data preview step
                    # fname = secure_filename(f[0].filename) if number_of_files == 1 else os.path.basename(filePath)
                    fname = "{}.csv".format(model_id)  # if number_of_files == 1 else os.path.basename(filePath)
                    if number_of_files == 1:  # if the file doesn't upload in data preview step, save the file
                        file_name = "{}.csv".format(model_id)  # f[0].filename
                        filePath = os.path.join(df_location, secure_filename(file_name))
                        f[0].save(filePath)
            else:  # here in case we came from data processing page
                filePath = session['filepath']
                fname = get_file_name_with_ext(session['filepath'])

            # Remove empty columns
            data = Helper.remove_empty_columns(filePath)

            # Check if the dataset is enough
            count_row = data.shape[0]
            message = 'No'

            if (count_row < 5):
                message = 'Uploaded data document does not have enough data, the document must have minimum 50 records of data for accurate processing.'
                return render_template('applications/pages/dashboard.html',
                                       message=message,
                                       ds_source=ds_source, ds_goal=ds_goal,
                                       segment='createmodel')

            # Get the DS file header
            dataset_info = BaseController.get_dataset_info(filePath)
            headersArray = getcvsheader(filePath)
            # fname = secure_filename(f[0].filename)
            session['fname'] = fname

            return fname, filePath, headersArray, data, dataset_info, message

        except Exception as e:
            logging.error(e)
            abort(500)

    @staticmethod
    def get_remote_data_details(file_path):  # Same as above but it works on db and api connection
        try:
            filePath = file_path
            ds_source = session['ds_source']
            ds_goal = session['ds_goal']

            # Remove empty columns
            data = Helper.remove_empty_columns(filePath)

            # Check if the dataset if engough
            count_row = data.shape[0]
            message = 'No'

            if (count_row < 5):
                message = 'Uploaded data document does not have enough data, the document must have minimum 50 records of data for accurate processing.'
                return render_template('applications/pages/dashboard.html',
                                       message=message,
                                       ds_source=ds_source, ds_goal=ds_goal,
                                       segment='createmodel')

            # Get the DS file header
            dataset_info = BaseController.get_dataset_info(filePath)
            headersArray = getcvsheader(filePath)
            # fname = secure_filename(f[0].filename)
            fname = session['fname']

            return fname, filePath, headersArray, data, dataset_info, message

        except Exception as e:
            logging.error(e)
            abort(500)

    @staticmethod
    def prepare_query_results(request):
        host_name = request.form.get('host_name')
        username = request.form.get('username')
        password = request.form.get('password')
        database_name = request.form.get('database_name')
        sql_query = request.form.get('sql_query')
        data, file_location, count_row = export_mysql_query_to_csv(host_name, username, password, database_name,
                                                                   sql_query)

        if (count_row < 50):
            return render_template('applications/pages/dashboard.html',
                                   message='Uploaded data document does not have enough data, the document must have minimum 50 records of data for accurate processing.',
                                   segment='createmodel')
        # Get the DS file header
        session['fname'] = database_name + ".csv"
        message = 'No'
        filelocation = '%s' % (file_location)
        headersArray = getcvsheader(filelocation)

        return database_name, file_location, headersArray, count_row, data, message

    @staticmethod
    def prepare_api_results(request):
        api_url = request.form.get('api_url')
        request_type = request.form.get('request_type')
        root_node = request.form.get('root_node')
        request_parameters = request.form.get('request_parameters')
        file_location, data, count_row = export_api_respose_to_csv(api_url, request_type, root_node,
                                                                   request_parameters)

        if (count_row < 50):
            return render_template('applications/pages/dashboard.html',
                                   message='Uploaded data document does not have enough data, the document must have minimum 50 records of data for accurate processing.',
                                   segment='createmodel')
        # Get the DS file header
        session['fname'] = api_data_filename
        message = 'No'
        filelocation = '%s' % (file_location)
        headersArray = getcvsheader(filelocation)

        return api_data_filename, file_location, headersArray, data, count_row, message

    @staticmethod
    def analyse_request(request):
        session['ds_goal'] = None
        model_desc = request.form.get('text_value')
        basecontroller = BaseController()
        results = basecontroller.detectefittedmodels(model_desc.strip())
        return render_template('applications/pages/suggestions.html',
                               message='analysis_result', results=results,
                               segment='idea')

    @staticmethod
    def update_model_info(request):
        model_id = request.args.get('param')
        n = request.args.get('n')
        if (n == '1'):
            profile = BaseController.get_model_status(model_id)
            return render_template('applications/pages/updateinfo.html',
                                   message='You do not have any running model yet.', profile=profile,
                                   modid=model_id,
                                   segment='showdashboard')

        model_id = request.form.get('modid')
        model_name = request.form.get('mname')
        model_description = "{}".format(request.form.get('mdesc'))

        basecontroller = BaseController()
        updatemodelinfo = basecontroller.updatemodelinfo(model_id, model_name, model_description)

        return redirect(url_for('base_blueprint.showmodels'))

    @staticmethod
    def change_model_status(model_id):
        basecontroller = BaseController()
        suspendmodel = basecontroller.changemodelstatus(model_id)
        return redirect(url_for('base_blueprint.showmodels'))

    def deploy_model(model_id):
        basecontroller = BaseController()
        deploy_statu = basecontroller.deploymodel(model_id)
        return redirect(url_for('base_blueprint.showmodels', message=deploy_statu))

    def describe_dataset(self, request, ds_goal, ds_source):
        # -----Data source codes------
        # 1, CSV
        # 2, Database
        # 3, Google Sheets
        # 4, Saleforce
        # 11, Data Files
        # 12, API
        # 25, Object Detecting
        # 29, Face Detection

        try:
            if ds_source == '1':
                fname, filePath, headersArray, data, dataset_info, message = self.get_data_details(request)

            if ds_source == '2':
                database_name, file_location, headersArray, count_row, data, message = self.prepare_query_results(
                    request)
                fname, filePath, headersArray, data, dataset_info, message = self.get_remote_data_details(
                    file_location)

            if ds_source == '12':
                database_name, file_location, headersArray, data, count_row, message = BaseDirector.prepare_api_results(
                    request)
                fname, filePath, headersArray, data, dataset_info, message = self.get_remote_data_details(
                    file_location)

            sample_data = (data.sample(n=10))

            # Draw sample data
            sample_data_values = sample_data.values
            sample_header = dataset_info.columns.tolist()
            sample_header = numpy.array(sample_header)
            complex_column = []
            dataset_info_value = dataset_info.values
            dataset_info_value = dataset_info_value.flatten()

            for i in range(len(sample_header)):
                complex_column.append(str(sample_header[i]) + "\n" + str(dataset_info_value[i]))
            df = pd.DataFrame(sample_data_values, columns=sample_header)
            df_values = df.values
            flp = np.rot90(df_values)
            flp = np.flip(flp)
            fig = go.Figure(data=[go.Table(
                header=dict(values=complex_column,
                            line_color='darkslategray',
                            fill_color='lightskyblue',
                            align='left'),
                cells=dict(values=flp,  # 2nd column
                           line_color='darkslategray',
                           fill_color='lightcyan',
                           align='left'))
            ])
            # fig.show()
            session['filepath'] = filePath
            return render_template('applications/pages/datapreview.html', required_changes='None',
                                   message='data_info', filePath=filePath, segment="selectmodelgoal",
                                   col_width="{}%".format(round(100 / len(sample_header), 2)),
                                   dataset_info=dataset_info, sample_data=sample_data)
        except Exception as e:
            logging.error(e)
            abort(500)
