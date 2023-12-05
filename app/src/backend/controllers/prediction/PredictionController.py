import logging
import os
import pathlib
import pickle
import random
import shutil
import time
from datetime import datetime

import numpy
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from flask import session
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from app import db, config_parser
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.core.ModelProcessor import ModelProcessor
from app.src.backend.utiles.Helper import Helper
from app.src.backend.utiles.db.datamanipulation.AdjustDataFrame import convert_data_to_sample
from app.src.backend.utiles.db.datamanipulation.AdjustDataFrame import remove_null_values
from app.src.backend.utiles.db.datamanipulation.DataCoderProcessor import DataCoderProcessor
from app.src.backend.utiles.db.db_helper.AttributesHelper import add_features, add_labels, delete_encoded_columns, get_features
from app.src.backend.utiles.db.db_helper.AttributesHelper import get_labels, add_api_details, \
    update_api_details_id
from app.src.backend.core.engine.mlmodels.Prediction import Prediction
from app.src.backend.utiles.CVSReader import get_only_file_name, randomize_csv_rows
from app.src.backend.utiles.CVSReader import getcvsheader, get_new_headers_list, reorder_csv_file
from app.src.backend.constants.BM_CONSTANTS import pkls_location, scalars_location, html_plots_location, \
    html_short_path, df_location, plot_locations, plot_zip_locations
from app.src.backend.models.ModelProfile import ModelProfile



# importing packages
import seaborn as sns
import matplotlib.pyplot as plt

class PredictionController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def saveDSFile(self):
        return 'file uploaded successfully'

    def run_prediction_model(self, root_path, csv_file_location, featuresdvalues, predicted_columns, ds_source, ds_goal,
                             demo):
        return self._create_prediction_model(root_path, csv_file_location, featuresdvalues, predicted_columns,
                                             ds_source, ds_goal)

    def predict_values_from_model(self, model_id, testing_values):
        try:
            # ------------------Predict values from the model-------------------------#
            #model = pickle.load(open(pkls_location + str(model_id) + '/' + str(model_id) + '_model.pkl', 'rb'))

            # Encode the testing values
            features_list = get_features(model_id)
            lables_list = get_labels(model_id)
            dcp = DataCoderProcessor()
            testing_values_dic = {}
            testing_values = numpy.array(testing_values)
            # testing_values = testing_values.reshape(1, len(testing_values))
            df_testing_values = pd.DataFrame(testing_values)
            encode_df_testing_values = dcp.encode_input_values(model_id, features_list, testing_values)

            # Sclaing testing values
            scalar_file_name = scalars_location + str(model_id) + '/' + str(model_id) + '_scalear.sav'
            s_c = pickle.load(open(scalar_file_name, 'rb'))
            test_x = s_c.transform(encode_df_testing_values)

            prediction = Prediction()
            predicted_values = prediction.predictlabels(model_id, test_x)
            #predicted_values = [model.predict(test_x)]  # ---
            # predicted_values = predicted_values.flatten()
            decoded_predicted_values = dcp.decode_output_values(model_id, lables_list, predicted_values)
            print(decoded_predicted_values)
            return decoded_predicted_values

        except Exception as e:
            logging.error(e)
            [['Entered data is far from any possible prediction, please refine the input data'], ['error']]

    def _create_prediction_model(self, root_path, csv_file_location, featuresdvalues, predicted_columns, ds_source,
                                 ds_goal):
        try:
            # ------------------Preparing data frame-------------------------#

            model_id = Helper.generate_id() # get_only_file_name(csv_file_location)
            # Rename the file coming from my dataset to data folder to model_id
            try:
                new_path = f"{df_location}{model_id}.csv"
                os.rename(csv_file_location, new_path)
                print(f"File {csv_file_location} has been successfully renamed to {model_id}")
            except FileNotFoundError:
                print(f"Error: File {csv_file_location} not found in folder {df_location}.")
            except FileExistsError:
                print(f"Error: A file with the name {model_id}.csv already exists in folder {df_location}.")

            csv_file_location = new_path
            shuffle_dataset = randomize_csv_rows(csv_file_location)
            cvs_header = getcvsheader(csv_file_location)
            new_headers_list = get_new_headers_list(cvs_header, predicted_columns)
            reordered_data = reorder_csv_file(csv_file_location, new_headers_list)
            data = reordered_data  # pd.read_csv(csv_file_location)
            new_headers_list = np.append(featuresdvalues, predicted_columns.flatten())
            data = data[new_headers_list]

            file_extension = pathlib.Path(csv_file_location).suffix
            newfilename = os.path.join(df_location, str(model_id) + file_extension)
            os.rename(csv_file_location, newfilename)
            file_name = get_only_file_name(newfilename)

            initiate_model = BaseController.initiate_model(model_id)

            # Determine features and lables
            features_last_index = len(new_headers_list) - (len(predicted_columns))
            model_features = new_headers_list[0:features_last_index]
            model_labels = predicted_columns

            # 1-Clean the data frame
            data = remove_null_values(data)
            if (len(data) == 0):  # No data found after cleaning
                return 0

            min_values = data.min(numeric_only=True)
            max_values = data.max(numeric_only=True)

            # 2- Encode the data frame
            deleteencodedcolumns = delete_encoded_columns(model_id)

            data_column_count = len(data.columns)
            testing_values_len = data_column_count - len(predicted_columns)

            # take slice from the dataset, all rows, and cloumns from 0:8
            features_df = data[model_features]
            labels_df = data[model_labels]

            real_x = data.loc[:, model_features]
            real_y = data.loc[:, model_labels]
            obj_features_dtypes = real_x.select_dtypes(include=object).dtypes
            obj_labels_dtypes = real_y.select_dtypes(include=object).dtypes
            # obj_features_dtypes = real_y.dtypes[real_x.dtypes != 'int64'][real_x.dtypes != 'float64']  # check if features has object values
            # obj_labels_dtypes = real_y.dtypes[real_y.dtypes != 'int64'][real_y.dtypes != 'float64'] # check if labels has object values

            dcp = DataCoderProcessor()
            real_x = dcp.encode_features(model_id, real_x)
            real_y = dcp.encode_labels(model_id, real_y)
            # remove rows with non values
            encoded_data = pd.concat((real_x, real_y), axis=1, join='inner')
            encoded_data = encoded_data.dropna(axis=0).reset_index(drop=True)

            real_x = encoded_data[model_features]
            real_y = encoded_data[model_labels]

            training_x, testing_x, training_y, testing_y = train_test_split(real_x, real_y, test_size=0.2,
                                                                            random_state=0)

            # Add standard scalar
            s_c = StandardScaler(with_mean=False)  # test
            training_x = s_c.fit_transform(training_x)
            test_x = s_c.transform(testing_x)
            file_name = get_only_file_name(csv_file_location)
            scalar_file_name = scalars_location + str(model_id) + '/' + str(model_id) + '_scalear.sav'
            pickle.dump(s_c, open(scalar_file_name, 'wb'))

            # Building the model
            start = time.time()
            logging.info("Start building the model:{}".format(str(start)))
            modelprocessor = ModelProcessor()
            # cls, y_pred, Root_Mean_Square_error, hidden_layer_size = modelprocessor._predictionmodelselector(training_x,
            #                                                                                                  training_y,
            #                                                                                                  test_x,
            #                                                                                                  testing_y,
            #                                                                                                  model_features,
            #                                                                                                  model_labels,
            #                                                                                                  obj_labels_dtypes)
            prediction_model = Prediction()
            cls, y_pred, Root_Mean_Square_error, hidden_layer_size = prediction_model.createmodel(model_id,
                                                                                                  encoded_data,
                                                                                                  model_features,
                                                                                                  model_labels)

            end = time.time()
            logging.info("End building the model:{}".format(str(end)))

            model_file_name = pkls_location + str(model_id) + '/' + str(model_id) + '_model.pkl'
            pickle.dump(cls, open(model_file_name, 'wb'))

            # Evaluating the Algorithm
            Mean_Absolute_Error = round(
                metrics.mean_absolute_error(numpy.array(testing_y, dtype=object), numpy.array(y_pred, dtype=object)),
                2)
            Mean_Squared_Error = round(metrics.mean_squared_error(testing_y, y_pred) * 100, 2) if (
                    round(metrics.mean_squared_error(testing_y, y_pred) * 100, 2) < 100) else 99
            c_m = ''

            # Show prediction
            x_range = np.linspace(real_x.min(), real_x.max())
            bb = x_range.reshape(-1, 1)
            y_range = cls.predict(x_range)
            fig = px.scatter(training_x, opacity=0.65)
            fig.add_traces(go.Scatter(x=x_range, y=y_range, name='Regression Fit'))
            # Add plotin files folder
            ploting_path = html_plots_location + str(model_id) + '/'
            html_file_location = ploting_path + str(model_id) + ".html"
            html_path = html_short_path + str(model_id) + '/' + str(model_id) + ".html"
            plotly.offline.plot(fig, filename=html_file_location, config={'displayModeBar': False}, auto_open=False)
            image_db_path = html_path

            # Comment creation of all photos zip file
            for i in (0, 1):  # range(len(model_features)):
                for j in range(len(model_labels)):
                    img_prefix = '_' + model_features[i] + '_' + model_labels[j]
                    plot_image_path = os.path.join(plot_locations, str(model_id) + '/' +
                                                   str(model_id) + img_prefix + '_plot.png')
                    sns.pairplot(data, x_vars=model_features[i],
                                 y_vars=model_labels[j], size=4, aspect=1, kind='scatter')
                    plot_image = plot_image_path  # os.path.join(root_path, 'static/images/plots/', get_only_file_name(csv_file_location) + '_plot.png')
                    plt.savefig(plot_image, dpi=300, bbox_inches='tight')

            # Create Zip folder
            zip_path = plot_zip_locations + str(model_id) + '/'
            shutil.make_archive(zip_path + str(model_id), 'zip', "{0}{1}{2}".format(plot_locations, model_id, "/"))
            #plt.show()

            # ------------------Predict values from the model-------------------------#
            now = datetime.now()
            sec = end - start
            number_sec = sec
            if number_sec < 1.0:
                time_duration = "Less than 1 sec"
            else:
                seconds = sec
                seconds = seconds % (24 * 3600)
                hour = seconds // 3600
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60
                time_duration = "%d:%02d:%02d" % (hour, minutes, seconds)

            all_return_values = {'model_id': model_id,
                                 'model_name': file_name,
                                 'running_duration': str(time_duration), 'confusion_matrix': c_m,
                                 'plot_image_path': image_db_path,  # image_path,
                                 'file_name': file_name,
                                 'Mean_Absolute_Error': Mean_Absolute_Error,
                                 'Mean_Squared_Error': Mean_Squared_Error,
                                 'Root_Mean_Squared_Error': Root_Mean_Square_error,
                                 'Accuracy': Mean_Squared_Error,
                                 'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                                 'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                                 'last_run_time': now.strftime("%d/%m/%Y %H:%M:%S"),
                                 'description': 'No description added yet.'}

            # Add model profile to the database
            modelmodel = {'model_id': model_id,
                          'model_name': file_name,
                          'user_id': session['logger'],
                          'model_headers': str(cvs_header)[1:-1],
                          'running_duration': str(time_duration),
                          'mean_absolute_error': str(Mean_Absolute_Error),
                          'mean_squared_error': str(Mean_Squared_Error),
                          'root_mean_squared_error': str(Root_Mean_Square_error),
                          'accuracy': str(Mean_Squared_Error),
                          'plot_image_path': image_db_path,
                          'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'last_run_time': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'ds_source': ds_source,
                          'ds_goal': ds_goal,
                          'status': config_parser.get('ModelStatus', 'ModelStatus.active'),
                          'deployed': config_parser.get('DeploymentStatus', 'DeploymentStatus.notdeployed'),
                          'description': 'No description added yet.'}
            model_model = ModelProfile(**modelmodel)
            db.session.commit()
            # Add new profile
            db.session.add(model_model)
            db.session.commit()

            # Add features, labels, and APIs details
            add_features_list = add_features(model_id, model_features)
            add_labels_list = add_labels(model_id, model_labels)
            api_details_id = random.randint(0, 22)
            api_details_list = add_api_details(model_id, api_details_id, 'v1')
            api_details_list = update_api_details_id(api_details_id)

            convert_data_to_sample(newfilename, 5)
            return all_return_values

        except  Exception as e:
            db.session.rollback()
            print(e)
            base_controller = BaseController()
            return base_controller.deletemodel(model_id)