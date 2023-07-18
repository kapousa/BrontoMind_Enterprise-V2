import logging

import numpy
import pandas as pd
from flask import render_template, session

from app.modules.base.app_routes.directors import ClassificationDirector
from app.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path, root_path, df_location, demo_key, \
    docs_templates_folder, output_docs
from app.modules.base.db_models.ModelAPIDetails import ModelAPIDetails
from app.modules.base.db_models.ModelProfile import ModelProfile
from app.bck.bm.apis.v1.APIHelper import APIHelper
from app.bck.bm.controllers.ControllersHelper import ControllersHelper
from app.bck.bm.controllers.prediction.PredictionController import PredictionController
from app.bck.bm.datamanipulation.DataCoderProcessor import DataCoderProcessor
from app.bck.bm.db_helper.AttributesHelper import get_labels, get_features
from app.bck.bm.utiles.CVSReader import improve_data_file


class PredictionDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def fetch_data(self, fname, headersArray, message):
        return render_template('applications/pages/prediction/selectfields.html', headersArray=headersArray,
                               fname=fname,
                               ds_source=session['ds_source'], ds_goal=session['ds_goal'],
                               segment='createmodel', message=message)

    def creatingthemodel(self, request, fname, ds_goal, ds_source):
        """
        Prepare the features and lablels before start creating the model
        @param request:
        @param fname:
        @param ds_goal:
        @param ds_source:
        @return:
        """
        predictionvalues = numpy.array((request.form.getlist('predcitedvalues')))
        featuresdvalues = numpy.array((request.form.getlist('featuresdvalues')))

        return render_template('applications/pages/prediction/creatingpredictionmodel.html',
                               predictionvalues=predictionvalues,
                               featuresdvalues=featuresdvalues,
                               progress_icon_path=progress_icon_path, fname=fname,
                               loading_icon_path=loading_icon_path,
                               ds_source=ds_source, ds_goal=ds_goal,
                               segment='createmodel')

    def complete_the_model(self, request):
        try:
            """
            Create the prediction model and show the model status dashboard
            @param request:
            @return:
            """
            fname = request.form.get('fname')
            ds_source = request.form.get('ds_source')
            ds_goal = request.form.get('ds_goal')
            location_details = {
                'host': request.form.get('location'),
                'username': request.form.get('name'),
                'password': request.form.get('session_token')
            }
            is_local_data = 'csv'  # request.form.get('is_local_data') if session['is_local_data'] != 'csv' else session['is_local_data']
            if (is_local_data != 'csv'):
                controllershelper = ControllersHelper()
                fname = "data"
                datafilepath = controllershelper.extract_data_fromphyfiles(fname)

            data_file_path = "%s%s" % (df_location, fname)
            df = pd.read_csv(data_file_path, sep=",")
            df_columns = df.columns
            data_sample = (df.sample(n=5))
            predictionvalues = numpy.array((request.form.get('predcitedvalues')).split(","))#numpy.array((request.form.getlist('predcitedvalues')))
            featuresdvalues = numpy.array(list(set(df_columns).difference(predictionvalues)))
            idf = improve_data_file(fname, df_location, predictionvalues)

            # run model
            obj_features_dtype = predictionvalues.dtype.name  # check if features has object values
            obj_labels_dtype = featuresdvalues.dtype.name
            aa = obj_labels_dtype.find('str')
            if (len(predictionvalues) == 1 and len(featuresdvalues) == 1) and (
                    obj_features_dtype.find('str') > -1 and obj_labels_dtype.find('str') > -1):
                classification_director = ClassificationDirector()
                session['ds_goal'] = '10'
                session['is_local_data'] = 'csv'
                return classification_director.create_text_classification_model(request)

            modelcontroller = PredictionController()
            model_controller = modelcontroller.run_prediction_model(root_path, data_file_path, featuresdvalues,
                                                                    predictionvalues, ds_source,
                                                                    ds_goal, demo_key)

            if model_controller == 0:
                return render_template('page-501.html',
                                       error="There is no enugh data to build the model after removing empty rows. The data set should have mimimum 50 records to buld the model.",
                                       segment='error')

            if model_controller == -1:
                return render_template('page-501.html',
                                       error="Error while creeating the model",
                                       segment='error')

            # Webpage details
            page_url = request.host_url + "predictevalues?t=" + str(ds_goal) + "&s=" + str(ds_source) + "&m=" + str(
                model_controller['model_id'])
            page_embed = "<iframe width='500' height='500' src='" + page_url + "'></iframe>"

            # APIs details and create APIs document
            model_api_details = ModelAPIDetails.query.filter_by(model_id=str(model_controller['model_id'])).first()
            apihelper = APIHelper()
            model_head = ModelProfile.query.with_entities(ModelProfile.model_id, ModelProfile.model_name).filter_by(
                model_id=model_controller['model_id']).first()
            generate_apis_docs = apihelper.generateapisdocs(model_head.model_id,
                                                            str(request.host_url + 'api/' + model_api_details.api_version),
                                                            docs_templates_folder, output_docs)

            return render_template('applications/pages/prediction/modelstatus.html',
                                   Accuracy=model_controller['Accuracy'],
                                   confusion_matrix=model_controller['confusion_matrix'],
                                   plot_image_path=model_controller['plot_image_path'], sample_data=[
                    data_sample.to_html(border=0, classes='table table-hover', header="false",
                                        justify="center").replace(
                        "<th>", "<th class='text-warning'>")],
                                   Mean_Absolute_Error=model_controller['Mean_Absolute_Error'], running_duration=model_controller['running_duration'],
                                   Mean_Squared_Error=model_controller['Mean_Squared_Error'], Running_Duration=model_controller['running_duration'],
                                   Root_Mean_Squared_Error=model_controller['Root_Mean_Squared_Error'],
                                   segment='createmodel', page_url=page_url, page_embed=page_embed,
                                   created_on=model_controller['created_on'], Description=model_controller['description'],
                                   updated_on=model_controller['updated_on'],
                                   last_run_time=model_controller['last_run_time'],
                                   fname=model_controller['file_name'], model_id=model_controller['model_id'])

        except Exception as e:
            logging.error(e)
            return render_template('page-501.html', error=e, segment='error')

    def predict_labels(self, request):
        try:
            ds_goal = request.args.get("t")
            ds_source = request.args.get("s")
            model_id = request.args.get("m")
            features_list = get_features(model_id)
            labels_list = get_labels(model_id)
            testing_values = []
            opt_param = len(request.form)
            datacoderprocessor = DataCoderProcessor()
            all_gategories_values = datacoderprocessor.get_all_categories_values(model_id)

            if opt_param == 0:
                # response = make_response()
                return render_template('applications/pages/prediction/predictevalues.html', features_list=features_list,
                                       labels_list=labels_list, ds_goal=ds_goal, mid=model_id, ds_source=ds_source,
                                       predicted_value='nothing', testing_values='nothing',
                                       all_gategories_values=all_gategories_values, predicted='Nothing', message='No')
            else:
                if request.method == 'POST':
                    for i in features_list:
                        feature_value = request.form.get(i)
                        # final_feature_value = float(feature_value) if feature_value.isnumeric() else feature_value
                        final_feature_value = feature_value
                        testing_values.append(final_feature_value)
                    modelcontroller = PredictionController()
                    predicted_value = modelcontroller.predict_values_from_model(model_id, testing_values)
                    # response = make_response()

                    if (predicted_value[0][0] == 'Entered data is far from any possible prediction, please refine the input data' or predicted_value[0] == 'Entered data is far from any possible prediction, please refine the input data' ):
                        return render_template('applications/pages/prediction/predictevalues.html',
                                               features_list=features_list,
                                               labels_list=labels_list, ds_goal=ds_goal, ds_source= ds_source, mid= model_id,
                                               predicted_value=predicted_value[0][0], testing_values=testing_values,
                                               all_gategories_values=all_gategories_values, predicted='NoValue',
                                               message='No')

                    return render_template('applications/pages/prediction/predictevalues.html',
                                           features_list=features_list,
                                           labels_list=labels_list, ds_goal=ds_goal, mid=model_id, ds_source=ds_source,
                                           predicted_value=predicted_value, testing_values=testing_values,
                                           all_gategories_values=all_gategories_values, predicted='Yes', message='No')
        except Exception as e:
            return render_template('applications/pages/nomodeltopredictevalues.html',
                                   error=str(e), ds_goal=ds_goal, mid=model_id, ds_source=ds_source,
                                   message="Entered data is far from any possible prediction, please refine the input data",
                                   segment='message')
