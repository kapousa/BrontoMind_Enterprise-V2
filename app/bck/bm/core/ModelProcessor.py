#  Copyright (c) 2021. Slonos Labs. All rights Reserved.
import logging

import numpy as np
from pandas import DataFrame
from sklearn import metrics
from sklearn.cluster import KMeans, estimate_bandwidth, MeanShift
from sklearn.linear_model import Lasso, LogisticRegression
from sklearn.linear_model import SGDRegressor, SGDClassifier, LinearRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR, LinearSVC, SVC

from app import config_parser
from app.bck.bm.controllers.clustering.ClusteringControllerHelper import ClusteringControllerHelper


class ModelProcessor:
    test_value = ''

    def __init__(self):
        self.test_value = '_'

    def createthemodel(self, df: DataFrame, modellabels, training_x, training_y, test_x, testing_y, model_features,
                       model_labels, obj_labels_dtypes):
        number_of_predictions = len(modellabels.axes[1])
        numberofrecords = len(df.axes[0])
        numberofrecordsedge = 100000
        labeldatatype = modellabels.dtypes

        if (numberofrecords <= 50):  # no enough data
            logging.error("Error: Model cannot be created because the length of the data is less than 50 records.")
            raise Exception("Error: Model cannot be created because the length of the data is less than 50 records.")

        if len(model_labels) == 0:  #  clustering
            if numberofrecords < 1000:
                logging.error("Error: Model cannot be created because of small dataset (10K record minimum required).")
                raise Exception(
                    "Error: Model cannot be created because of small dataset (10K record minimum required).")
            else:
                # Create clustering model
                bandwidth = estimate_bandwidth(training_x, quantile=0.3)
                cls = MeanShift(bandwidth=bandwidth).fit(training_x)
                clusters = cls.labels_

        if len(obj_labels_dtypes) != 0:  # predict category
            cls = KMeans(n_clusters=2, random_state=0)
            return cls

        # if (number_of_predictions == 1 and labeldatatype[0] == np.object):  # Classification
        #     cls = KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2)
        #     return cls

        if (number_of_predictions > 0):  # Multi-Output Classification
            cls = LinearRegression()
            # cls = MultiOutputClassifier(KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2), n_jobs=-1)
            return cls

        cls = LinearRegression()  # Prediction
        return cls

        # if (number_of_predictions == 1):
        #     if (labeldatatype[0] == np.object):  # Classification
        #         if (numberofrecords < numberofrecordsedge):
        #             try:
        #                 cls = make_pipeline(StandardScaler(), SGDClassifier(max_iter=1000, tol=1e-3))
        #             except:
        #                 cls = SGDClassifier(max_iter=5)
        #         else:
        #             try:
        #                 cls = make_pipeline(StandardScaler(), LinearSVC(random_state=0, tol=1e-5))
        #             except:
        #                 cls = GaussianNB()
        #     else:  # Prediction (Regression)
        #         if (labeldatatype[0] == np.int64 and numberofrecords < numberofrecordsedge):
        #             cls = SGDRegressor()
        #         elif (labeldatatype[0] == np.int64 and numberofrecords >= numberofrecordsedge):
        #             if (number_of_features < 10):
        #                 cls = Lasso(alpha=1.0)
        #             else:
        #                 try:
        #                     cls = SVR(kernal='linear')
        #                 except:
        #                     cls = SVR(kernal='rbf')
        #         else:
        #             cls = MultiOutputClassifier(KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2), n_jobs=-1)
        # else:
        #     cls = MultiOutputClassifier(KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2),
        #                                 n_jobs=-1)

    def classificationmodelselector(self, numberofrecords):
        numberofrecordsedge = 100000

        # Classification
        if (numberofrecords < numberofrecordsedge):
            try:
                cls = LinearSVC(verbose=0)
                LinearSVC(C=1.0, class_weight=None, dual=True, fit_intercept=True,
                          intercept_scaling=1, loss='squared_hinge', max_iter=1000,
                          multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
                          verbose=0)
                return cls
            except:
                try:
                    cls = KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2)
                    return cls
                except:
                    try:
                        cls = SVC(probability=True, decision_function_shape='ovo', kernel='rbf', gamma=0.0078125, C=8)
                        return cls
                    except Exception as e:
                        print(e)
                        return 0

        if (numberofrecords >= numberofrecordsedge):
            try:
                cls = SGDClassifier(max_iter=1000, tol=0.01)
                return cls
            except Exception as e:
                print(e)
                return 0
        return 0

    def _predictionmodelselector(self, training_x, training_y, test_x, testing_y, model_features, model_labels,
                                 obj_labels_dtypes):
        accuracy = 0.0
        num_layers = 5
        if len(model_features) == 1 and len(model_labels) == 1 and len(obj_labels_dtypes) == 0:
            cls = LinearRegression().fit(training_x, training_y)
            y_pred = cls.predict(test_x)
            Root_Mean_Squared_Error = 99 if (
                    (round(np.sqrt(metrics.mean_squared_error(testing_y, y_pred)), 2)) >= 99) else round(
                np.sqrt(metrics.mean_squared_error(testing_y, y_pred)), 2)
            accuracy = round(Root_Mean_Squared_Error * 100, 2)
        elif len(model_labels) == 1 and len(obj_labels_dtypes) == 0:
            cls = LogisticRegression().fit(training_x, training_y)
            #cls = Lasso(alpha=0.01).fit(training_x, training_y)
            y_pred = cls.predict(test_x)
            # accuracy = confusion_matrix(testing_y, y_pred, normalize=True) #round((metrics.accuracy_score(testing_y, y_pred, normalize=True) * 100), 2) #round((cls.score(test_x, testing_y) * 100), 2)
            accuracy = round(np.sqrt(metrics.mean_squared_error(testing_y, y_pred)), 2)  # Root_Mean_Square_error
        else:
            # Add on March 21, 2023, to solve unknown label type error
            training_y = training_y.values.astype('float64')
            training_x = training_x.astype('float64')
            hidden_layer_size = 64
            layers_arr = []
            acc_arry = []

            # while True:
            # cls = MLPClassifier(hidden_layer_sizes=(hidden_layer_size, hidden_layer_size, hidden_layer_size), activation="relu", random_state=None, max_iter=2000)
            # cls = cls.fit(training_x, training_y)

            # Define an MLP classifier with 3 outputs
            cls = MLPClassifier(hidden_layer_sizes=(64, 16, 32), max_iter=500, solver="sgd", momentum=False,
                                nesterovs_momentum=False)

            # Wrap the MLP classifier in a MultiOutputRegressor
            cls = MultiOutputRegressor(cls).fit(training_x, training_y)

            # Compute the average feature weights across all outputs
            # total_weights = np.zeros_like(cls.estimators_[0].coefs_[0])
            # for estimator in cls.estimators_:
            #     for i, layer_weights in enumerate(estimator.coefs_):
            #         total_weights += layer_weights
            # avg_weights = total_weights / len(cls.estimators_)

            # Print the average feature weights
            # print("Average feature weights:")
            # print(avg_weights)

            y_pred = cls.predict(test_x)
            # c_m = confusion_matrix(testing_y, y_pred)

            acc = cls.score(training_x,
                            training_y)  # round((metrics.accuracy_score(testing_y, y_pred, normalize=True) * 100), 2) #cross_val_score(cls, training_x, training_y, cv=5) #
            layers_arr.append(hidden_layer_size)
            acc_arry.append(acc)
            accuracy = np.max(acc_arry)  # gettting best accuracy
            used_layer_index = acc_arry.index(accuracy)
            num_layers = layers_arr[used_layer_index]  # geting number of layers of best accuracy
            accuracy = round(accuracy * 100, 2)

        return cls, y_pred, accuracy, num_layers

    def predictionmodelselector_(self, df: DataFrame, modelfeatures, modellabels):
        number_of_predictions = len(modellabels.axes[1])
        number_of_features = len(modelfeatures.axes[1])
        numberoflabels = modellabels
        numberofrecords = len(df.axes[0])
        numberofrecordsedge = 100000
        if (number_of_predictions == 1):
            labeldatatype = modellabels.dtypes
            # Prediction (Regression)
            if ((labeldatatype[0] == np.int64 or labeldatatype[
                0] == np.float) and numberofrecords < numberofrecordsedge):
                cls = SGDRegressor()
            elif ((labeldatatype[0] == np.int64 or labeldatatype[
                0] == np.float) and numberofrecords >= numberofrecordsedge):
                if (number_of_features < 10):
                    cls = Lasso(alpha=1.0)
                else:
                    try:
                        cls = SVR(kernal='linear')
                    except:
                        cls = SVR(kernal='rbf')
            else:
                cls = MultiOutputClassifier(KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2),
                                            n_jobs=-1)
        else:
            cls = MultiOutputClassifier(KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2),
                                        n_jobs=-1)
        return cls

    def clustering_model_selector(self, df_scaled):
        try:
            df_scaled = df_scaled.reshape(len(df_scaled), 1)
            clustering_controller_helper = ClusteringControllerHelper()
            no_of_clusters = clustering_controller_helper.calculate_no_clusters(df_scaled)
            cls = KMeans(
                n_clusters=no_of_clusters)
            return cls, no_of_clusters
        except Exception as e:
            return config_parser.get('ErrorMessages', 'ErrorMessages.fail_create_model')
