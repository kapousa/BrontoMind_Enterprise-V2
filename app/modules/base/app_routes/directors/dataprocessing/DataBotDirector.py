import logging
import os

import pandas as pd
from flask import render_template, abort, session, send_file
from werkzeug.utils import secure_filename

from app.constants.BM_CONSTANTS import tempfiles_loaction
from app.bck.bm.controllers.dataprocessing.DataBotController import DataBotController
from app.bck.bm.utiles.CVSReader import get_file_name_with_ext
from app.constants.DATAPROCESSING_CONSTANTS import modified_files_temp_path


class DataBotDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def data_prepration_bot(self, request, message="None"):
        try:
            return render_template('applications/pages/dataprocessing/databot/uploaddata.html', segment='preparedata',
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
            return render_template('applications/pages/dataprocessing/databot/databot.html', segment='preparedata',
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
            return render_template('applications/pages/dataprocessing/databot/databot.html', segment='preparedata',
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
                                   segment='preparedata',
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
            return render_template('applications/pages/datapreview.html', segment='preparedata',
                                   user_text=user_text, required_changes=required_changes, request_type="draft",
                                   response_head="We understand that the following actions should be taken in response to yourn words: ",
                                   response_footer="Check out the table below to see how your data will look after you make these changes.",
                                   message='data_info', sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace("<th>", "<th class='text-warning'>")], )
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)
