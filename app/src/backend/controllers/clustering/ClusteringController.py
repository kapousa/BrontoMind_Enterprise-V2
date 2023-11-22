import os
import pathlib
import pickle
import random
from datetime import datetime

import pandas as pd
# from app import config_parser
from flask import session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.utils import shuffle

from app import db, config_parser
from app.src.backend.constants import app_root_path
from app.src.backend.models.ModelProfile import ModelProfile
from app.src.backend.constants import pkls_location, data_files_folder, df_location
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.controllers.ControllersHelper import ControllersHelper
from app.src.backend.controllers.clustering.ClusteringControllerHelper import ClusteringControllerHelper
from app.src.backend.core.ModelProcessor import ModelProcessor
from app.src.backend.utiles.db.db_helper.AttributesHelper import add_features, add_labels, add_api_details, \
    update_api_details_id
from app.src.backend.utiles.CVSReader import get_only_file_name
from app.src.backend.utiles.Helper import Helper


class ClusteringController:
    members = []

    file_name = config_parser.get('SystemConfigurations', 'SystemConfigurations.default_data_file_prefix')

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']
        self.file_name = (self.file_name).replace("'", "")

    def get_data_cluster(self, model_id, data):
        """
        Get the correct cluster of provided data and related keywords
        @param data:
        @return: clusters, keywords
        """
        try:
            # load the vectorizer
            vic_filename = '%s%s%s' % (pkls_location, str(model_id), '/vectorized_pkl.pkl')
            vectorizer = pickle.load(open(vic_filename, 'rb'))

            # Load the model
            model_file_name = "{0}{1}/{2}_model.pkl".format(pkls_location, str(model_id), str(model_id))
            cls = pickle.load(open(model_file_name, 'rb'))

            # Get custer/s
            clusters = cls.predict(vectorizer.transform(data))

            # Get clusters keywords
            keywords = []
            clusters_dic = {}
            for cluster in clusters:
                keywords.append(ClusteringControllerHelper.get_cluster_keywords(cluster))

            for i in range(len(clusters)):
                keywords_str = keywords[i]
                cluster_key = 'Cluster_' + str(clusters[i])
                clusters_dic[cluster_key] = keywords_str

            return clusters_dic
        except  Exception as e:
            return 0

    def run_clustering_model(self, location_details, ds_goal, ds_source, is_local_data, featuresdvalues=['data']):
        try:
            # ------------------Preparing data frame-------------------------#
            model_id =  Helper.generate_model_id()
            initiate_model = BaseController.initiate_model(model_id)
            helper = Helper()

            # Prepare the date and creating the clustering model
            clusteringcontrollerhelper = ClusteringControllerHelper()
            files_path = '%s%s%s%s' % (app_root_path, data_files_folder, str(model_id),
                                       '_files')  # this code need to be rephrase to find how to get local data for new model
            csv_file_path = '%s%s' % (df_location, session['fname'])
            file_extension = pathlib.Path(csv_file_path).suffix
            newfilename = os.path.join(df_location, str(model_id) + file_extension)
            os.rename(csv_file_path, newfilename)
            csv_file_path = newfilename
            file_name = get_only_file_name(csv_file_path)

            # Create datafile (data.pkl)
            if (is_local_data == 'Yes'):
                folders_list = ControllersHelper.get_folder_structure(files_path, req_extensions=('.txt'))
                featuresdvalues = ['data']
                data_set = clusteringcontrollerhelper.create_clustering_data_set(files_path)
            elif (is_local_data == 'csv'):
                data_set = clusteringcontrollerhelper.create_clustering_csv_data_set(str(model_id), csv_file_path,
                                                                                     featuresdvalues)
            else:
                folders_list = helper.list_ftp_dirs(
                    location_details)
                data_set = clusteringcontrollerhelper.create_clustering_FTP_data_set(location_details)

            full_file_path = '%s%s%s%s%s%s' % (
                app_root_path, data_files_folder, str(model_id), '/', str(model_id), '.pkl')

            X_train = pd.read_pickle(full_file_path)
            X_train['data'] = X_train[X_train.columns[0:]].apply(
                lambda x: ','.join(x.dropna().astype(str)),
                axis=1
            )
            X_train = X_train[['data']]
            X_train = shuffle(X_train)
            documents = X_train['data'].values.astype("U") #X_train[featuresdvalues].values.astype("U") #This line have been commenteded to enable build model using more than one feature
            documents = documents.flatten()  #This line have been commenteded to enable build model using more than one feature
            features = []
            vectorizer = TfidfVectorizer(stop_words='english')

            features = vectorizer.fit_transform(documents)

            # Store vectorized
            vic_filename = '%s%s%s%s' % (pkls_location, str(model_id), '/', 'vectorized_pkl.pkl')
            pickle.dump(vectorizer, open(vic_filename, 'wb'))

            # Select proper model
            mp = ModelProcessor()
            cls, no_of_clusters = mp.clustering_model_selector(features.data)
            model = cls.fit(features)
            y_pred = cls.predict(features)


            # evaluate the model
            # Calculate SSE
            sse = model.inertia_
            # Calculate silhouette score
            silhouette = round(silhouette_score(features, model.labels_) * 100, 2)
            # Calculate Calinski-Harabasz index
            #ch = calinski_harabasz_score(features, model.labels_)

            print(f"SSE: {sse:.2f}")
            print(f"Silhouette score: {silhouette:.2f}")
            #print(f"Calinski-Harabasz index: {ch:.2f}")

            # Update data with related cluster
            X_train['cluster'] = model.labels_
            data_file_location = ClusteringControllerHelper.generate_labeled_datafile(str(model_id),
                                                                                      model.labels_)  # Add label column to orginal data file

            model_file_name = pkls_location + str(model_id) + '/' + str(model_id) + '_model.pkl'
            pickle.dump(cls, open(model_file_name, 'wb'))

            # Show Elbow graph and get clusters' keywords
            html_path = ClusteringControllerHelper.plot_elbow_graph(features.data, str(model_id))
            #html_path = ClusteringControllerHelper.plot_clustering_report(features.data, model, model.labels_, file_name)
            html_path = ClusteringControllerHelper.plot_model_clusters(str(model_id), features, y_pred)
            clusters_keywords = ClusteringControllerHelper.extract_clusters_keywords(model, no_of_clusters, vectorizer)

            # ------------------Predict values from the model-------------------------#
            now = datetime.now()
            all_return_values = {'file_name': str(model_id),
                                 'clusters_keywords': clusters_keywords,
                                 'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                                 'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                                 'last_run_time': now.strftime("%d/%m/%Y %H:%M:%S"),
                                 'data_file_location': data_file_location,
                                 'model_id': model_id,
                                 'model_name': str(model_id),
                                 'status': config_parser.get('ModelStatus', 'ModelStatus.active'),
                                 'deployed': config_parser.get('DeploymentStatus', 'DeploymentStatus.notdeployed'),
                                 'description': 'No description added yet.',
                                 'Accuracy': str(silhouette)
                                 }

            # Add model profile to the database
            modelmodel = {'model_id': model_id,
                          'model_name': str(model_id),
                          'user_id': 1,
                          'model_headers': 'str(cvs_header)[1:-1]',
                          'prediction_results_accuracy': 'str(c_m)',
                          'mean_absolute_error': 'str(Mean_Absolute_Error)',
                          'mean_squared_error': 'str(Mean_Squared_Error)',
                          'root_mean_squared_error': 'str(Root_Mean_Squared_Error)',
                          'plot_image_path': html_path,
                          'accuracy': str(silhouette),
                          'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'last_run_time': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'ds_source': ds_source,
                          'ds_goal': ds_goal,
                          'status': config_parser.get('ModelStatus', 'ModelStatus.active'),
                          'deployed': config_parser.get('DeploymentStatus', 'DeploymentStatus.notdeployed'),
                          'description': 'No description added yet.'}
            model_model = ModelProfile(**modelmodel)
            # Add new profile
            db.session.add(model_model)
            db.session.commit()

            # Add features, labels, and APIs details
            add_features_list = add_features(model_id, ['input'])
            add_labels_list = add_labels(model_id, ['cluster', 'keywords'])
            api_details_id = random.randint(0, 22)
            api_details_list = add_api_details(model_id, api_details_id, 'v1')
            api_details_list = update_api_details_id(api_details_id)

            # APIs details and create APIs document

            return all_return_values
        except Exception as e:
            print(e)
            return {}
            # return config_parser.get('ErrorMessages', 'ErrorMessages.fail_create_model')
