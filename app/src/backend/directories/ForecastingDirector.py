import pandas as pd
from flask import render_template
from markupsafe import Markup

from app.src.backend.constants import df_location, docs_templates_folder, \
    output_docs
from app.src.backend.models.ModelAPIDetails import ModelAPIDetails

from app.src.backend.models.ModelProfile import ModelProfile
from app.src.backend.apisservices.v1.APIHelper import APIHelper
from app.src.backend.controllers.mlforecasting.MLForecastingController import MLForecastingController
from app.src.backend.controllers.timeforecasting.TimeForecastingController import TimeForecastingController


class ForecastingDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def specify_forecating_properties(self, file_location, headersArray, message):
        time_forecasting_controller = TimeForecastingController()
        forecasting_columns, depended_columns, datetime_columns = time_forecasting_controller.analyize_dataset(
            file_location)
        message = (message if ((len(forecasting_columns) != 0) and (
                len(datetime_columns) != 0) and (
                                       len(depended_columns) != 0)) else 'Your data file doesn not have one or more required fields to build the timeforecasting model. The file should have:<ul><li>One or more ctaegoires columns</li><li>One or more time series columns</li><li>One or more columns with numerical values.</li></ul><br/>Please check your file and upload it again.')
        return render_template('applications/pages/forecasting/dsfileanalysis.html',
                               headersArray=headersArray,
                               segment='createmodel', message=Markup(message),
                               forecasting_columns=forecasting_columns,
                               depended_columns=depended_columns,
                               datetime_columns=datetime_columns)

    def create_forecasting_model(self, request):
        fname = request.form.get('fname')
        ds_source = request.form.get('ds_source')
        ds_goal = request.form.get('ds_goal')
        data_file_path = "%s%s" % (df_location, fname)
        df = pd.read_csv(data_file_path, sep=",")
        data_sample = (df.sample(n=5))

        ml_forecasting_controller = MLForecastingController()
        forecastingfactor = request.form.get('forecastingfactor')
        dependedfactor = request.form.get('dependedfactor')
        timefactor = request.form.get('timefactor')
        all_return_values = ml_forecasting_controller.run_mlforecasting_model(
            data_file_path, forecastingfactor,
            dependedfactor, timefactor, ds_source, ds_goal)
        # Forecasting webpage details
        page_url = request.host_url + "embedforecasting?m=" + str(all_return_values['model_id'])
        page_embed = "<iframe width='500' height='500' src='" + page_url + "'></iframe>"

        # APIs details and create APIs document
        model_api_details = ModelAPIDetails.query.filter_by( model_id = str(all_return_values['model_id'])).first()
        apihelper = APIHelper()
        model_head = ModelProfile.query.with_entities(ModelProfile.model_id, ModelProfile.model_name).filter_by(
            model_id=all_return_values['model_id']).first()
        generate_apis_docs = apihelper.generateapisdocs(model_head.model_id,
                                                        str(request.host_url + 'api/' + model_api_details.api_version),
                                                        docs_templates_folder, output_docs)

        return render_template('applications/pages/forecasting/modelstatus.html',
                               depended_factor=all_return_values['depended_factor'],
                               forecasting_category=all_return_values['forecasting_factor'],
                               plot_image_path=all_return_values['plot_image_path'],
                               sample_data=[
                                   data_sample.to_html(border=0, classes='table table-hover', header="false",
                                                       justify="center").replace("<th>",
                                                                                 "<th class='text-warning'>")],
                               fname=model_head.model_name, model_id = model_head.model_id,
                               segment='createmodel', page_url=page_url, page_embed=page_embed,
                               created_on=all_return_values['created_on'],
                               updated_on=all_return_values['updated_on'],
                               last_run_time=all_return_values['last_run_time'],
                               description=all_return_values['description']
                               )