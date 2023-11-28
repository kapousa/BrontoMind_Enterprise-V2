# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import subprocess
import io
import os
import shutil
import sys

from werkzeug.utils import secure_filename

import numpy
import pandas as pd
from flask import session, g, url_for, send_from_directory
from flask import redirect, send_file, Response, Flask, \
    current_app
from flask import render_template, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from matplotlib.backends.backend_template import FigureCanvas

from app import login_manager
from app.src.backend.modules.base import blueprint
from app.src.backend.directories.BaseDirector import BaseDirector
from app.src.backend.directories.ClassificationDirector import ClassificationDirector
from app.src.backend.directories.ClusteringDirector import ClusteringDirector
from app.src.backend.directories.LocalDatasetsDirector import LocalDatasetsDirector
from app.src.backend.directories.ForecastingDirector import ForecastingDirector
from app.src.backend.directories.PredictionDirector import PredictionDirector
from app.src.backend.constants.BM_CONSTANTS import plot_zip_download_location, progress_icon_path, loading_icon_path, \
    tempfiles_loaction
from app.src.backend.models.ModelProfile import ModelProfile
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.core.DocumentProcessor import DocumentProcessor
from app.src.backend.core.engine.factories.ClassificationFactory import ClassificationFactory
from app.src.backend.core.engine.factories.ClusteringFactory import ClusteringFactory
from app.src.backend.core.engine.factories.ForecastingFactory import ForecastingFactory
from app.src.backend.core.engine.factories.PredictionFactory import PredictionFactory
from app.src.backend.utiles.Helper import Helper
from app.src.backend.utiles.db.datamanipulation.AdjustDataFrame import create_figure
from app.src.backend.utiles.CVSReader import getcvsheader, adjust_csv_file
from app.src.backend.utiles.CVSReader import improve_data_file

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = 'app/data/'
app.config['DOCS_TEMPLATES_FOLDER'] = 'static/docs_templates/'
app.config['APPS_DATA_FOLDER'] = 'app/static/docs_templates/apps_data_sources'
app.config['DOWNLOAD_APPS_DATA_FOLDER'] = 'static/docs_templates/apps_data_sources'
app.config['OUTPUT_DOCS'] = 'static/output_docs/'
app.config['OUTPUT_PDF_DOCS'] = 'static/output_docs/'
app.config['DEMO_KEY'] = 'DEMO'
app.config['APP_ROOT'] = '/app'
root_path = app.root_path


@blueprint.route('/projects')
@login_required
def projects():
    return BaseDirector.load_home(request)

@blueprint.route('/index')
@login_required
def index():
    return render_template('base/index.html', segment='index')

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/base/FILE.html
        return render_template("base/" + template, segment=segment)

    except TemplateNotFound:
        #return render_template('base/page-404.html'), 404
        return render_template('page-404.html'), 404
    except:
        # return render_template('base/page-500.html'), 500
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

@blueprint.route('/preparedata')
@login_required
def preparedata():
    return render_template('applications/pages/comingsoon.html', segment='preparedata')

@blueprint.route('/computervision')
@login_required
def computervision():
    return render_template('applications/pages/computervision.html', segment='computervision')

@blueprint.route('/selectmodelgoal')
@login_required
def selectmodelgoal():
    return render_template('applications/pages/selectmodelgoal.html', segment='selectmodelgoal')

@blueprint.route('/analyserequest', methods=['POST'])
@login_required
def analyserequest():
    basedirector = BaseDirector()
    return basedirector.analyse_request(request)

@blueprint.route('/idea')
@login_required
def idea():
    return render_template('applications/pages/idea.html', segment='idea')

@blueprint.route('/createmodel')
@login_required
def createmodel():
    ds_goal = request.args.get("t")
    session['ds_goal'] = ds_goal
    return render_template('applications/pages/selectdssource.html', ds_goal=ds_goal, segment='selectmodelgoal')

@blueprint.route('/updatemodel')
@login_required
def updatemodel():
    model_profile_row = ModelProfile.query.all()
    session['ds_goal'] = model_profile_row['ds_goal']
    return render_template('applications/pages/selectdssource.html', segment='createmodel')

@blueprint.route('/selectcsvds', methods=['GET', 'POST'])
@login_required
def selectcsvds():
    session['ds_source'] = request.form.get('ds_source')
    return selectds()

@blueprint.route('/selectmysqlds', methods=['GET', 'POST'])
@login_required
def selectmysqlds():
    session['ds_source'] = request.form.get('ds_source')
    return selectds()

@blueprint.route('/selectsfds', methods=['GET', 'POST'])
@login_required
def selectsfds():
    session['ds_source'] = request.form.get('ds_source')
    return selectds()

@blueprint.route('/selectgsds', methods=['GET', 'POST'])
@login_required
def selectgsds():
    session['ds_source'] = request.form.get('ds_source')
    return selectds()

@blueprint.route('/selectphysicalfiles', methods=['GET', 'POST'])
@login_required
def selectphysicalfiles():
    session['ds_source'] = request.form.get('ds_source')
    return selectds()

@blueprint.route('/callapi', methods=['GET', 'POST'])
@login_required
def callapi():
    session['ds_source'] = request.form.get('ds_source')
    return selectds()

def selectds():
    return render_template('applications/pages/connecttods.html', ds_id=session['ds_source'], segment='createmodel')

@blueprint.route('/previewdata', methods=['GET', 'POST'])
@login_required
def preview_data():
    ds_source = session['ds_source']
    ds_goal = session['ds_goal']
    base_director = BaseDirector()
    return base_director.describe_dataset(request, ds_goal, ds_source)

@blueprint.route('/uploadcsvds', methods=['GET', 'POST'])
@login_required
def uploadcsvds():
    if request.method == 'POST':
        fname, filePath, headersArray, data, dataset_info, message = BaseDirector.get_data_details(request)

        # remove sessions files path
        temp_file_location = "{}{}".format(tempfiles_loaction, fname)
        if 'filepath' in session and os.path.exists(session['filepath']):  # Delete temp file
            if os.path.exists(temp_file_location):
                os.remove("{}{}".format(tempfiles_loaction, fname))
            session.pop('filepath')
        if 'secondaryfilepath' in session and os.path.exists(session['secondaryfilepath']):  # Delete merging file
            if os.path.exists(session['secondaryfilepath']):
                os.remove(session['secondaryfilepath'])
            session.pop('secondaryfilepath')

        cc = session['ds_goal']
        if (session['ds_goal'] == current_app.config['PREDICTION_MODULE']):  # Prediction
            prediction_director = PredictionDirector()
            return prediction_director.fetch_data(fname, headersArray, message)

        if (session['ds_goal'] == current_app.config['CLASSIFICATION_MODULE']):  # Classification
            session['fname'] = fname
            return render_template('applications/pages/classification/selectfields.html', headersArray=headersArray,
                                   segment='selectmodelgoal', message=message, fname=fname,
                                   ds_source=session['ds_source'], ds_goal=session['ds_goal'])

        if (session['ds_goal'] == current_app.config['FORECASTING_MODULE']):  # Forecasting
            forecasting_director = ForecastingDirector()
            return forecasting_director.specify_forecating_properties(filePath, headersArray, message)

        if (session['ds_goal'] == current_app.config['CLUSTERING_MODULE']):
            session['fname'] = fname
            return render_template('applications/pages/clustering/selectfields.html', headersArray=headersArray,
                                   segment='selectmodelgoal', message=message)

        if (session['ds_goal'] == current_app.config['ROBOTIC_MODULE']):  # Robotics
            return render_template('applications/pages/robotics/selectfields.html', headersArray=headersArray,
                                   fname=fname,
                                   ds_source=session['ds_source'], ds_goal=session['ds_goal'],
                                   segment='selectmodelgoal', message=message)

        # ds_goal = '' means user can't decide
        document_processor = DocumentProcessor()
        columns_list, nan_cols, final_columns_list, final_total_rows, numric_columns, datetime_columns = document_processor.document_analyzer(
            filePath)
        return render_template('applications/pages/analysisreport.html', headersArray=headersArray,
                               columns_list=columns_list, nan_cols=nan_cols,
                               final_columns_list=final_columns_list, final_total_rows=final_total_rows,
                               numric_columns=numric_columns,
                               datetime_columns=datetime_columns,
                               fname=fname,
                               ds_source=session['ds_source'], ds_goal=session['ds_goal'],
                               segment='selectmodelgoal', message=message)

@blueprint.route('/dffromdb', methods=['GET', 'POST'])
@login_required
def dffromdb():
    try:
        if request.method == 'POST':
            #database_name, file_location, headersArray, count_row, message = BaseDirector.prepare_query_results(request)
            fname, filePath, headersArray, data, dataset_info, message = BaseDirector.get_data_details(request)

            if (session['ds_goal'] == current_app.config['PREDICTION_MODULE']):
                prediction_director = PredictionDirector()
                return prediction_director.fetch_data(session['fname'], headersArray, message)

            if (session['ds_goal'] == current_app.config['FORECASTING_MODULE']):
                forecasting_director = ForecastingDirector()
                return forecasting_director.specify_forecating_properties(filePath, headersArray, message)

            if (session['ds_goal'] == current_app.config['CLASSIFICATION_MODULE']):
                return render_template('applications/pages/classification/selectfields.html', headersArray=headersArray,
                                       segment='selectmodelgoal', message=message)

            if (session['ds_goal'] == current_app.config['CLUSTERING_MODULE']):
                return render_template('applications/pages/clustering/selectfields.html', headersArray=headersArray,
                                       segment='selectmodelgoal', message=message)

            if (session['ds_goal'] == current_app.config['ROBOTIC_MODULE']):
                return render_template('applications/dashboard.html')

            return render_template('applications/dashboard.html')

    except Exception as e:
        print(e)
        return render_template('page-501.html', error=e, segment='error')

@blueprint.route('/dffromapi', methods=['GET', 'POST'])
@login_required
def dffromapi():
    try:
        if request.method == 'POST':

            #database_name, file_location, headersArray, count_row, message = BaseDirector.prepare_api_results(request)
            fname, filePath, headersArray, data, dataset_info, message = BaseDirector.get_data_details(request)

            if (session['ds_goal'] == current_app.config['PREDICTION_MODULE']):
                prediction_director = PredictionDirector()
                return prediction_director.fetch_data(session['fname'], headersArray, message)

            if (session['ds_goal'] == current_app.config['FORECASTING_MODULE']):
                forecasting_director = ForecastingDirector()
                return forecasting_director.specify_forecating_properties(filePath, headersArray, message)

            if (session['ds_goal'] == current_app.config['CLASSIFICATION_MODULE']):
                return render_template('applications/pages/classification/selectfields.html', headersArray=headersArray,
                                       segment='selectmodelgoal', message=message)

            if (session['ds_goal'] == current_app.config['CLUSTERING_MODULE']):
                return render_template('applications/pages/clustering/selectfields.html', headersArray=headersArray,
                                       segment='selectmodelgoal', message=message)

            if (session['ds_goal'] == current_app.config['ROBOTIC_MODULE']):
                return render_template('applications/dashboard.html')

            return render_template('applications/dashboard.html')

    except Exception as e:
        print(e)
        return render_template('page-501.html', error='Error calling the API', segment='error')

@blueprint.route('/creatingthemodel', methods=['GET', 'POST'])
@login_required
def creatingthemodel():  # The function of showing the gif page
    try:
        if request.method == 'POST':
            ds_source = session['ds_source']
            ds_goal = session['ds_goal']

            if (ds_goal == current_app.config[
                'CLASSIFICATION_MODULE'] and ds_source == '11'):  # data source: Physical files
                ftb_server = request.form.get('ftb_server')
                ftb_username = request.form.get('ftb_username')
                ftb_password = request.form.get('ftb_password')
                is_local_data = request.form.get("is_local_data")
                session['is_local_data'] = request.form.get("is_local_data")
                classification_label = numpy.array(request.form.getlist('classification_label'))
                classification_features = numpy.array(request.form.getlist('classification_features'))
                return render_template('applications/pages/classification/creatingclassificationmodel.html',
                                       location=ftb_server,
                                       name=ftb_username,
                                       session_token=ftb_password,
                                       progress_icon_path=progress_icon_path, fname='',
                                       is_local_data=is_local_data,
                                       loading_icon_path=loading_icon_path,
                                       classification_label=classification_label,
                                       classification_features=classification_features,
                                       ds_source=ds_source, ds_goal=ds_goal,
                                       segment='selectmodelgoal')

            fname = session['fname']

            if (ds_goal == current_app.config['PREDICTION_MODULE']):
                predication_director = PredictionDirector()
                return predication_director.creatingthemodel(request, fname, ds_goal, ds_source)

            if (ds_goal == current_app.config['CLASSIFICATION_MODULE']):
                classification_label = numpy.array(request.form.getlist('classification_label'))
                classification_features = numpy.array(request.form.getlist('classification_features'))
                acf = adjust_csv_file(session['fname'], classification_features, classification_label)
                session['is_local_data'] = request.form.get("is_local_data")
                return render_template('applications/pages/classification/creatingclassificationmodel.html',
                                       classification_label=classification_label,
                                       classification_features=classification_features,
                                       progress_icon_path=progress_icon_path, fname=fname,
                                       loading_icon_path=loading_icon_path,
                                       ds_source=ds_source, ds_goal=ds_goal,
                                       segment='selectmodelgoal')

            if (ds_goal == current_app.config['FORECASTING_MODULE']):
                timefactor = request.form.get('timefactor')
                forecastingfactor = request.form.get('forecastingfactor')
                dependedfactor = request.form.get('dependedfactor')
                return render_template('applications/pages/forecasting/creatingforecastingmodel.html',
                                       timefactor=timefactor, dependedfactor=dependedfactor,
                                       forecastingfactor=forecastingfactor,
                                       progress_icon_path=progress_icon_path, fname=fname,
                                       loading_icon_path=loading_icon_path,
                                       ds_source=ds_source, ds_goal=ds_goal,
                                       segment='selectmodelgoal')

            if (ds_goal == current_app.config['CLUSTERING_MODULE']):
                clustering_features = numpy.array(request.form.getlist('clustering_features'))
                session['is_local_data'] = request.form.get("is_local_data")
                return render_template('applications/pages/clustering/creatingclusteringmodel.html',
                                       clustering_features=clustering_features,
                                       progress_icon_path=progress_icon_path, fname=fname,
                                       loading_icon_path=loading_icon_path,
                                       ds_source=ds_source, ds_goal=ds_goal,
                                       segment='selectmodelgoal')

            return 0
        else:
            return 0
    except Exception as e:

        tb = sys.exc_info()[2]
        print(e)
        return render_template('page-501.html', error=e.with_traceback(tb))

@blueprint.route('/sendvalues', methods=['GET', 'POST'])
@login_required
def sendvalues():  # The main function of creating the model
    try:
        if request.method == 'POST':

            ds_source = session['ds_source']
            ds_goal = session['ds_goal']
            g.user = current_user.get_id()

            if (ds_goal == current_app.config['CLASSIFICATION_MODULE'] and ds_source == '11'):
                classificationfactory = ClassificationFactory()
                return classificationfactory.create_classification_text_model(request)

            fname = session['fname']

            if (ds_goal == current_app.config['PREDICTION_MODULE']):
                predictionfactory = PredictionFactory()
                return predictionfactory.create_prediction_csv_model(request)

            if (ds_goal == current_app.config['CLASSIFICATION_MODULE']):
                classification_label = numpy.array(request.form.getlist('classification_label'))
                idf = improve_data_file(fname, app.config['UPLOAD_FOLDER'],
                                        classification_label)  # Reorder the columns of the data file
                classificationfactory = ClassificationFactory()
                return classificationfactory.create_classification_text_model(request)

            if (ds_goal == current_app.config['CLUSTERING_MODULE']):
                clusteringfactory = ClusteringFactory()
                return clusteringfactory.create_clustering_text_model(request)

            if (ds_goal == current_app.config['FORECASTING_MODULE']):
                forecastingfactory = ForecastingFactory()
                return forecastingfactory.create_forecasting_csv_model(request)

            return 0
    except Exception as e:
        return render_template('page-501.html',
                               error="Error loading data, please try again to load the data",
                               segment='error')

@blueprint.route('/runthemodel', methods=['GET', 'POST'])
@login_required
def runthemodel():
    try:
        ds_source = request.form.get('ds_source')
        return redirect('pages/connecttods.html', ds_id=ds_source, segment='selectmodelgoal')

    except Exception as e:
        print(e)
        return render_template('page-501.html', error=e.with_traceback(), segment='error')

@app.route('/plot.png')
@login_required
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png', segment='selectmodelgoal')

@blueprint.route('/predictevalues', methods=['GET', 'POST'])
def predictevalues():
    try:
        model_id = request.args.get('m')
        model_status = BaseController.get_model_status(model_id)

        if (len(model_status) == 0):
            return render_template('applications/pages/nomodeltopredictevalues.html',
                                   message='There is no active model')

        ds_goal = request.args.get("t")

        if (ds_goal == current_app.config['PREDICTION_MODULE']):
            prediction_director = PredictionDirector()
            return prediction_director.predict_labels(request)

        if (ds_goal == current_app.config['CLASSIFICATION_MODULE']):
            classification_directory = ClassificationDirector()
            return classification_directory.classify_inputs_from_model(request)

    except Exception as e:
        return render_template('applications/pages/nomodeltopredictevalues.html',
                               error=str(e),
                               message="Not able to predict. One or more entered values has not relevant value in your dataset, please enter data from provided dataset",
                               segment='message')

@blueprint.route('/embedforecasting', methods=['GET', 'POST'])
def embedforecasting():
    try:
        model_id = request.args.get("m")
        profile = BaseController.get_model_status(model_id)
        if len(profile) == 0:
            # response = make_response()
            return render_template('applications/pages/forecasting/embedforecasting.html',
                                   message='There is no active model')
        else:
            # Forecasting webpage details
            page_url = request.host_url + "embedforecasting?m=" + str(profile['model_id'])
            page_embed = "<iframe width='500' height='500' src='" + page_url + "'></iframe>"
            return render_template('applications/pages/forecasting/embedforecasting.html',
                                   depended_factor=profile['depended_factor'],
                                   forecasting_factor=profile['forecasting_category'],
                                   plot_image_path=profile['plot_image_path'], message='No', )
    except Exception as e:
        print(e)
        return render_template('page-501.html',
                               error='Not able to predict. One or more entered values has not relevant value in your dataset, please enter data from provided dataset',
                               segment='message')

@blueprint.route('/showmodels')
@login_required
def showmodels():
    profiles = BaseController.get_all_models()
    call_message = request.args.get('message')
    if len(profiles) > 0:
        return render_template('applications/pages/models.html', message='No', profiles=profiles,
                               segment='showmodels', call_message=call_message)

    return render_template('applications/pages/models.html', message='You do not have any active model yet.',
                               segment='showmodels')

@blueprint.route('/showdashboard')
@login_required
def showdashboard():
    model_id = request.args.get('param')
    profile = BaseController.get_model_status(model_id)

    if len(profile) > 0:

        if (profile['ds_goal'] == current_app.config['CLASSIFICATION_MODULE'] and str(profile['ds_source']) == '11'):
            classification_director = ClassificationDirector()
            return classification_director.show_text_model_dashboard(model_id)

        if profile['ds_goal'] == current_app.config['CLASSIFICATION_MODULE']:
            # Webpage details
            classification_director = ClassificationDirector()
            return classification_director.show_text_model_dashboard(model_id)

        if profile['ds_goal'] == current_app.config['CLUSTERING_MODULE']:
            clustering_director = ClusteringDirector()
            return clustering_director.show_clustermodel_dashboard(request, profile)

        if profile['ds_goal'] == current_app.config['ROBOTIC_MODULE']:
            return redirect(url_for('cvision_blueprint.showobjdetectemodel', model_id=model_id))

        fname = str(profile['model_id']) + '.csv'
        data_file_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        df = pd.read_csv(data_file_path, sep=",")
        data_sample = (df.sample(n=5, replace=True))

        if profile['ds_goal'] == current_app.config['PREDICTION_MODULE']:
            # Webpage details
            page_url = request.host_url + "predictevalues?t=" + str(profile['ds_goal']) + "&s=" + str(
                profile["ds_source"]) + "&m=" + str(profile['model_id'])
            page_embed = "<iframe width='500' height='500' src='" + page_url + "'></iframe>"
            return render_template('applications/pages/prediction/dashboard.html',
                                   Accuracy=profile['accuracy'], running_duration=profile['running_duration'],
                                   confusion_matrix='', model_id=profile['model_id'],
                                   plot_image_path=profile['plot_image_path'], sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace(
                        "<th>", "<th class='text-warning'>")], Mean_Absolute_Error=profile['mean_absolute_error'],
                                   Mean_Squared_Error=profile['mean_squared_error'],
                                   Root_Mean_Squared_Error=profile['root_mean_squared_error'], message='No',
                                   fname=profile['model_name'], page_url=page_url, page_embed=page_embed,
                                   segment='showdashboard', created_on=profile['created_on'],
                                   ds_goal=profile['ds_goal'], Description=profile['description'],
                                   updated_on=profile['updated_on'], last_run_time=profile['last_run_time'])

        if profile['ds_goal'] == current_app.config['CLASSIFICATION_MODULE']:
            # Webpage details
            page_url = request.host_url + "predictevalues?m=" + profile['model_id']
            page_embed = "<iframe width='500' height='500' src='" + page_url + "'></iframe>"
            return render_template('applications/pages/classification/dashboard.html',
                                   accuracy=profile['prediction_results_accuracy'],
                                   confusion_matrix='',
                                   plot_image_path=profile['plot_image_path'], sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace(
                        "<th>", "<th class='text-warning'>")], Mean_Absolute_Error=profile['mean_absolute_error'],
                                   Mean_Squared_Error=profile['mean_squared_error'],
                                   Root_Mean_Squared_Error=profile['root_mean_squared_error'], message='No',
                                   fname=profile['model_name'], page_url=page_url, page_embed=page_embed,
                                   segment='showdashboard', created_on=profile['created_on'],
                                   ds_goal=profile['ds_goal'],
                                   updated_on=profile['updated_on'], last_run_time=profile['last_run_time'])

        if profile['ds_goal'] == current_app.config['FORECASTING_MODULE']:
            # Forecasting webpage details
            page_url = request.host_url + "embedforecasting?m=" + str(profile['model_id'])
            page_embed = "<iframe width='500' height='500' src='" + page_url + "'></iframe>"
            return render_template('applications/pages/forecasting/dashboard.html',
                                   accuracy=profile['prediction_results_accuracy'], description=profile['description'],
                                   confusion_matrix='', depended_factor=profile['depended_factor'],
                                   forecasting_factor=profile['forecasting_category'],
                                   error_mse=profile['mean_squared_error'], model_id=profile['model_id'],
                                   plot_image_path=profile['plot_image_path'], sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace(
                        "<th>", "<th class='text-warning'>")], message='No',
                                   fname=profile['model_name'], page_url=page_url, page_embed=page_embed,
                                   segment='showdashboard', created_on=profile['created_on'],
                                   ds_goal=profile['ds_goal'],
                                   updated_on=profile['updated_on'], last_run_time=profile['last_run_time'])

        else:
            return 0
    else:
        return render_template('applications/pages/dashboard.html', message='You do not have any running model yet.',
                               segment='showdashboard')

@blueprint.route('/deletemodels', methods=['GET', 'POST'])
@login_required
def deletemodels():
    bc = BaseController()
    delete_model = bc.deletemodels()
    return redirect(url_for('base_blueprint.showmodels'))

@blueprint.route('<model_id>/deletemodel', methods=['GET','POST'])
@login_required
def deletemodel(model_id):
    bc = BaseController()
    delete_model = bc.deletemodel(model_id)
    return redirect(url_for('base_blueprint.showmodels'))

@blueprint.route('/updateinfo', methods=['GET', 'POST'])
@login_required
def updateinfo():
    return BaseDirector.update_model_info(request)

@blueprint.route('<model_id>/changemodelstatus', methods=['GET', 'POST'])
@login_required
def changemodelstatus(model_id):
    return BaseDirector.change_model_status(model_id)

@blueprint.route('<model_id>/deploymodel', methods=['GET', 'POST'])
@login_required
def deploymodel(model_id):
    return BaseDirector.deploy_model(model_id)

@blueprint.route('/applications', methods=['GET', 'POST'])
@login_required
def applications():
    return render_template('applications/applications.html', segment='applications')

@blueprint.route('/installapp', methods=['GET', 'POST'])
@login_required
def installapp():
    if request.method == 'POST':
        bc = BaseController()
        delete_model = bc.deletemodels()
        f = request.form.get('filename')
        original = os.path.join(app.config['APPS_DATA_FOLDER'], f)
        target = os.path.join(app.config['UPLOAD_FOLDER'], f)

        shutil.copyfile(original, target)

        # Remove empty columns
        data = pd.read_csv(target)
        data = data.dropna(axis=1, how='all')
        data.drop(data.columns[data.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
        data.to_csv(target, index=False)
        data = pd.read_csv(target)

        # Check if the dataset if engough
        count_row = data.shape[0]
        if (count_row > 50):
            # Get the DS file header
            headersArray = getcvsheader(target)
            fname = f
            return render_template('applications/pages/prediction/selectfields.html', headersArray=headersArray,
                                   fname=fname,
                                   segment='createmodel', message='No')
        else:
            return render_template('applications/pages/prediction/selectfields.html',
                                   message='Uploaded data document does not have enough data, the document must have minimum 50 records of data for accurate processing.',
                                   segment='createmodel')

@blueprint.route('/analysedata')
@login_required
def analysedata():
    session['ds_goal'] = '000'
    return render_template('applications/pages/selectdssource.html', segment='selectmodelgoal')

@blueprint.route('/downloaddsfile', methods=['GET', 'POST'])
@login_required
def downloaddsfile():
    if request.method == 'POST':
        f = request.form.get('filename')
        path = os.path.join(app.config['DOWNLOAD_APPS_DATA_FOLDER'], f)
        return send_file(path, as_attachment=True)

@blueprint.route('<model_id>/downloadapisdocument', methods=['GET', 'POST'])
@login_required
def downloadapisdocument(model_id):
    # # For windows you need to use drive name [ex: F:/Example.pdf]
    # fname = ModelProfile.query.with_entities(ModelProfile.model_name).first()[0]
    path = app.config['OUTPUT_PDF_DOCS'] + str(model_id) + '/' + str(model_id) + '_BrontoMind_APIs_document.docx'
    return send_from_directory(app.config['OUTPUT_PDF_DOCS'], str(model_id) + '/' + str(model_id) + '_BrontoMind_APIs_document.docx')

@blueprint.route('/<model_id>/downloadplots', methods=['GET', 'POST'])
@login_required
def downloadplots(model_id):
    # For windows, you need to use drive name [ex: F:/Example.pdf]
    path = plot_zip_download_location + model_id + '/' + model_id + '.zip'
    return send_file(path, as_attachment=True)

@blueprint.route('/uploaddatafiles', methods=['GET', 'POST'])
@login_required
def uploaddatafiles():
    if request.method == 'POST':
        # folderfiles = request.files.getlist('folderfiles[]')
        # mapfile = request.files['mapfile']
        ds_source = request.form.get('ds_source')
        ds_goal = request.form.get('ds_goal')
        classification_director = ClassificationDirector()
        return classification_director.create_text_classification_model(ds_goal)

@blueprint.route('/testyolo', methods=['GET', 'POST'])
def testyolo():

    pathh = "/Users/kapo/PycharmProjects/yolov5/detect.py"
    uploads_dir = "app/tmep/images"
    filename = "qwe.jpeg"
    subprocess.run("ls")
    subprocess.run(['python3', pathh, '0', os.path.join(uploads_dir, secure_filename(filename))])
    print("Done")
    return redirect(url_for('base_blueprint.idea'))

@blueprint.route('/datasets', methods=['GET', 'POST'])
@login_required
def datasets():
    return LocalDatasetsDirector.view_all()

@blueprint.route('/downlaoddataset/<id>', methods=['GET', 'POST'])
@login_required
def downlaoddataset(id):
    path = LocalDatasetsDirector.downlaod_datasets(id)
    return send_file(path, as_attachment=True)

## Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html', error="Access Forbidden - Please authenticate using Login page", segment='error'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html', error="Access Forbidden - Please authenticate using Login page", segment='error'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html', error="Page Not Found", segment='error'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template(('page-500.html'), error=error, segment='error'), 500
