import logging
import os
import shutil

import flask
import pandas as pd
from flask import render_template, abort, session, send_file
from werkzeug.utils import secure_filename

from app.bck.bm.controllers.BaseController import BaseController
from app.bck.bm.controllers.dataprocessing.CleanDataEngine import CleanDataEngine
from app.bck.bm.controllers.dataprocessing.DataCleanController import DataCleanController
from app.bck.bm.controllers.dataprocessing.DataMergeController import DataMergeController
from app.bck.bm.utiles.Helper import Helper
from app.constants.BM_CONSTANTS import tempfiles_loaction
from app.bck.bm.controllers.dataprocessing.DataBotController import DataBotController
from app.bck.bm.utiles.CVSReader import get_file_name_with_ext
from app.constants.DATAPROCESSING_CONSTANTS import modified_files_temp_path


class DataProcessingDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def data_prepration_bot(self, request, message="None"):
        try:
            return render_template('applications/pages/dataprocessing/databot/uploaddata.html',
                                   segment='selectmodelgoal',
                                   message=message)
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def build_data_sheet(self, request):
        try:
            f = request.files.getlist('filename[]')
            file_name = f[0].filename
            filepath = os.path.join(tempfiles_loaction, secure_filename(file_name))
            f[0].save(filepath)
            session['filepath'] = filepath
            df = pd.read_csv(filepath)
            data_sample = df.sample(n=10)
            return render_template('applications/pages/dataprocessing/databot/databot.html', segment='selectmodelgoal',
                                   required_changes=None,
                                   message='There is no active model', sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace("<th>", "<th class='text-warning'>")], )
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def preview_changes(self, request):
        try:
            user_text = request.form.get('user_text')
            session['user_text'] = user_text
            databotcontroller = DataBotController()
            required_changes, data_sample = databotcontroller.drafting_bot_request(user_text, session['filepath'])
            session['required_changes'] = required_changes
            return render_template('applications/pages/dataprocessing/databot/databot.html', segment='selectmodelgoal',
                                   user_text=user_text, required_changes=required_changes, request_type="draft",
                                   response_head="We understand that the following actions should be taken in response to yourn words: ",
                                   response_footer="Check out the table below to see how your data will look after you make these changes.",
                                   message='There is no active model', sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace("<th>", "<th class='text-warning'>")], )
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def apply_changes(self, request):
        try:
            filepath = session['filepath']
            user_text = session['user_text']
            required_changes = session['required_changes']
            databotcontroller = DataBotController()
            required_changes, data_sample = databotcontroller.apply_bot_request(filepath, required_changes)
            return render_template('applications/pages/dataprocessing/databot/databot.html',
                                   segment='selectmodelgoal',
                                   user_text=user_text, required_changes=required_changes, request_type="apply",
                                   response_head="The following actions have been taken in response to yourn words: ",
                                   response_footer="Check out the table below to see the new data look.",
                                   message='There is no active model', sample_data=[
                    data_sample.to_html(border=0,
                                        classes='table table-hover',
                                        header="false",
                                        justify="center").replace(
                        "<th>", "<th class='text-warning'>")], )
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def download_modifiedfile(self, request):
        try:
            f = session['filepath']
            file_name = get_file_name_with_ext(f)
            path = os.path.join("{0}{1}".format(modified_files_temp_path, file_name))
            return send_file(path, as_attachment=True)
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def cancel_modifiedfile(self, request):
        try:
            f = session['filepath']
            os.remove(f)
            session.pop('filepath', default=None)
            session.pop('required_changes', default=None)
            session.pop('user_text', default=None)
            return self.data_prepration_bot(request, "Changes have been canceled.")
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def preview_chat_changes(self, request):
        try:
            user_text = request.form.get('user_text')
            session['user_text'] = user_text
            databotcontroller = DataBotController()
            required_changes, data_sample = databotcontroller.drafting_bot_request(user_text, session['filepath'])
            session['required_changes'] = required_changes
            return render_template('applications/pages/dataprocessing/databot/chatprocessingresult.html',
                                   segment='selectmodelgoal', process='chat',
                                   user_text=user_text, required_changes=required_changes, request_type="draft",
                                   response_head="We understand that the following actions should be taken in response to yourn words: ",
                                   response_footer="Check out the table below to see how your data will look after you make these changes.",
                                   message='data_info', sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace("<th>", "<th class='text-warning'>")], )
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def apply_chat_changes(self, request):
        try:
            # Copy original file to temp folder
            filePath = session['filepath']
            file_name = get_file_name_with_ext(filePath)
            temp_file = os.path.join("{0}{1}".format(modified_files_temp_path, file_name))
            shutil.copy(filePath, temp_file)

            dataset_info = BaseController.get_dataset_info(filePath)

            # Sample data
            data = pd.read_csv(filePath)
            sample_data = (data.sample(n=10))
            sample_header = dataset_info.columns.tolist()

            return render_template('applications/pages/datapreview.html', required_changes='None',
                                   message='data_info', filePath=filePath, segment="selectmodelgoal",
                                   col_width="{}%".format(round(100 / len(sample_header), 2)),
                                   dataset_info=dataset_info, sample_data=sample_data)
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def preview_clean_changes(self, request):
        try:
            file_path = session['filepath']
            selected_options = []
            for i in range(0, 9):
                if len(request.form.getlist('customCheck{}'.format(i))) != 0:
                    selected_options.append(int(request.form.getlist('customCheck{}'.format(i))[0]))
            data_clean_controller = DataCleanController()
            data_sample = data_clean_controller.drafting_clean_request(selected_options, file_path)

            return render_template('applications/pages/dataprocessing/databot/cleanprocessingresult.html',
                                   segment='selectmodelgoal', process='chat', request_type="draft",
                                   message='data_info', sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace("<th>", "<th class='text-warning'>")], )
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def apply_clean_changes(self, request):
        try:
            # Copy original file to temp folder
            filePath = session['filepath']
            file_name = get_file_name_with_ext(filePath)
            temp_file = os.path.join("{0}{1}".format(modified_files_temp_path, file_name))
            shutil.copy(filePath, temp_file)

            dataset_info = BaseController.get_dataset_info(filePath)

            # Sample data
            data = pd.read_csv(filePath)
            sample_data = (data.sample(n=10))
            sample_header = dataset_info.columns.tolist()

            return render_template('applications/pages/datapreview.html', required_changes='None',
                                   message='data_info', filePath=filePath, segment="selectmodelgoal",
                                   col_width="{}%".format(round(100 / len(sample_header), 2)),
                                   dataset_info=dataset_info, sample_data=sample_data)
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def match_merging_fields(self, request):
        """ Match fields from main dataset and secondary dataset """
        try:
            secondary_data_file = request.files['secondarydatafile']  # request.form.get('secondarydatafile')

            # Save secondary data file
            file_name = get_file_name_with_ext(session['filepath'])
            secondary_file_path = os.path.join(tempfiles_loaction, "sec-{}".format(file_name))
            session['secondaryfilepath'] = secondary_file_path
            secondary_data_file.save(secondary_file_path)

            # Get columns list of each files
            original_columns = Helper.get_csv_columns(session['filepath'])
            secondary_columns = Helper.get_csv_columns(secondary_file_path)

            return render_template('applications/pages/dataprocessing/databot/matchfields.html',
                                   segment='selectmodelgoal', original_columns=original_columns,
                                   secondary_columns=secondary_columns,
                                   message='data_info')
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def preview_merge_changes(self, request):
        try:
            matchsensitivity = request.form.get("matchsensitivity")
            mergetype = request.form.get("mergetype")
            mergescore = request.form.get("mergescore")
            fields = int(request.form.get("fields"))
            original_matching_columns = []
            secondary_matching_columns = []

            for i in range(0, fields):  # Identify selected matching fields
                original_matching_columns.append(request.form.get("original{}".format(i)))
                secondary_matching_columns.append(request.form.get("secondary{}".format(i)))

            datamergecontroller = DataMergeController()
            data_sample = datamergecontroller.drafting_merge_request(session['filepath'],
                                                                     session['secondaryfilepath'],
                                                                     original_matching_columns,
                                                                     secondary_matching_columns,
                                                                     mergetype)

            if not isinstance(data_sample, str):
                return render_template('applications/pages/dataprocessing/databot/mergeprocessingresult.html',
                                       segment='selectmodelgoal', process='chat', request_type="draft",
                                       message='data_info', sample_data=[
                        data_sample.to_html(border=0, classes='table table-hover', header="false",
                                            justify="center").replace("<th>", "<th class='text-warning'>")], )
            else:
                return render_template('applications/pages/dataprocessing/databot/mergeprocessingresult.html',
                                       segment='selectmodelgoal', process='chat', request_type="draft",
                                       message=data_sample)

        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def apply_merge_changes(self, request):
        try:
            # Copy original file to temp folder
            filePath = session['filepath']
            file_name = get_file_name_with_ext(filePath)
            temp_file = os.path.join("{0}{1}".format(modified_files_temp_path, file_name))
            shutil.copy(filePath, temp_file)

            dataset_info = BaseController.get_dataset_info(filePath)

            # Sample data
            data = pd.read_csv(filePath)
            sample_data = (data.sample(n=10))
            sample_header = dataset_info.columns.tolist()

            return render_template('applications/pages/datapreview.html', required_changes='None',
                                   message='data_info', filePath=filePath, segment="selectmodelgoal",
                                   col_width="{}%".format(round(100 / len(sample_header), 2)),
                                   dataset_info=dataset_info, sample_data=sample_data)
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def cancel_changes(self, request):
        try:
            # Copy temp file to original folder
            filePath = session['filepath']
            file_name = get_file_name_with_ext(filePath)
            temp_file = os.path.join("{0}{1}".format(modified_files_temp_path, file_name))
            shutil.copy(temp_file, filePath)
            if 'secondaryfilepath' in session:      # Delete merging file
                os.remove(session['secondaryfilepath'])
            os.remove(temp_file)

            dataset_info = BaseController.get_dataset_info(filePath)

            # Sample data
            data = pd.read_csv(filePath)
            sample_data = (data.sample(n=10))
            sample_header = dataset_info.columns.tolist()

            return render_template('applications/pages/datapreview.html', required_changes='None',
                                   message='data_info', filePath=filePath, segment="selectmodelgoal",
                                   col_width="{}%".format(round(100 / len(sample_header), 2)),
                                   dataset_info=dataset_info, sample_data=sample_data)
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)
