import os
import pickle
import string
from ast import literal_eval
from random import shuffle

import matplotlib.pyplot as plt
import numpy
import numpy as np
import pandas as pd
import plotly as pl
import plotly.graph_objs as pgo
import seaborn as sns
from nltk.corpus import stopwords
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score, calinski_harabasz_score, silhouette_samples
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import MinMaxScaler

from app import config_parser
from app.src.backend.constants import html_plots_location, html_short_path, df_location, clusters_keywords_file, \
    output_docs_location, labeled_data_filename
from app.src.backend.utiles.Helper import Helper



class ClusteringControllerHelper:
    # stop_words = set(stopwords.words('english'))

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.stop_words = set(stopwords.words('english'))

    def plot_clustering_report_(self, df, model, label, model_name='file_name'):
        # Represent neighborhoods as in previous bubble chart, adding cluster information under color.
        df = pd.DataFrame(df)
        df['label'] = label

        x_axis = np.array(df[0])
        y_axis = np.array(df[1])
        x_center = numpy.array(model.cluster_centers_[:, 0])
        y_center = numpy.array(model.cluster_centers_[:, 1])
        u_label = np.unique(label)

        fig = plt.figure()
        # ax = fig.add_subplot(111)
        plt.scatter(x_axis, y_axis, s=50)
        plt.scatter(x_center, y_center, marker='x')
        fig.show()
        html_file_location = html_plots_location + model_name + ".html"
        html_path = html_short_path + model_name + ".html"
        pl.offline.plot(fig, filename=html_file_location, config={'displayModeBar': True}, auto_open=False)

        return html_path

    @staticmethod
    def plot_clustering_report(df, model, label, model_name='file_name'):
        # Represent neighborhoods as in previous bubble chart, adding cluster information under color.
        df = pd.DataFrame(df)
        df['label'] = label
        u_label = np.unique(label)
        trace_arr = []
        for i in u_label:
            label_data = df.loc[df['label'] == i]
            trace0 = pl.graph_objs.Scatter(x=label_data[0],
                                           y=label_data[1],
                                           mode="markers",
                                           name="Cluster:" + str(i),
                                           text="Cluster:" + str(i),
                                           marker=pgo.scatter.Marker(symbol='x',
                                                                     size=12,
                                                                     color=u_label, opacity=0.5),
                                           showlegend=True
                                           )
            trace_arr.append(trace0)

        # Represent cluster centers.
        trace1 = pl.graph_objs.Scatter(x=model.cluster_centers_[:, 0],
                                       y=model.cluster_centers_[:, 1],
                                       name='Center of the cluster',
                                       mode='markers',
                                       marker=pgo.scatter.Marker(symbol='x',
                                                                 size=12,
                                                                 color='black'),
                                       showlegend=True
                                       )
        trace_arr.append(trace1)

        layout5 = pgo.Layout(title='Data Clusters',
                             xaxis=pgo.layout.XAxis(showgrid=True,
                                                    zeroline=True,
                                                    showticklabels=True),
                             yaxis=pgo.layout.YAxis(showgrid=True,
                                                    zeroline=True,
                                                    showticklabels=True),
                             hovermode='closest')

        data7 = pgo.Data(trace_arr)
        layout7 = layout5
        layout7['title'] = 'Data Clusters'
        fig7 = pgo.Figure(data=data7, layout=layout7)

        # Plot model
        html_file_location = html_plots_location + model_name + ".html"
        html_path = html_short_path + model_name + ".html"
        fig = make_subplots(rows=2, cols=1)
        # 1- clusters
        for k in range(len(fig7.data)):
            fig.add_trace(fig7.data[k], row=1, col=1)
        # 2- Elbow graph
        # TODO: Add code to implent Elbow function and plot it with the clustering graph

        pl.offline.plot(fig, filename=html_file_location, config={'displayModeBar': False}, auto_open=False)

        return html_path

    @staticmethod
    def plot_data_points(df, model, label, model_name='file_name'):
        # Represent neighborhoods as in previous bubble chart, adding cluster information under color.
        df = pd.DataFrame(df)
        df['label'] = label
        u_label = np.unique(label)
        trace_arr = []
        for i in u_label:
            label_data = df.loc[df['label'] == i]
            trace0 = pl.graph_objs.Scatter(x=label_data[0],
                                           y=label_data[1],
                                           mode="markers",
                                           name="Cluster:" + str(i),
                                           text="Cluster:" + str(i),
                                           marker=pgo.scatter.Marker(symbol='x',
                                                                     size=12,
                                                                     color=u_label, opacity=0.5),
                                           showlegend=True
                                           )
            trace_arr.append(trace0)

        # Represent cluster centers.
        trace1 = pl.graph_objs.Scatter(x=model.cluster_centers_[:, 0],
                                       y=model.cluster_centers_[:, 1],
                                       name='Center of the cluster',
                                       mode='markers',
                                       marker=pgo.scatter.Marker(symbol='x',
                                                                 size=12,
                                                                 color='black'),
                                       showlegend=True
                                       )
        trace_arr.append(trace1)

        layout5 = pgo.Layout(title='Data Clusters',
                             xaxis=pgo.layout.XAxis(showgrid=True,
                                                    zeroline=True,
                                                    showticklabels=True),
                             yaxis=pgo.layout.YAxis(showgrid=True,
                                                    zeroline=True,
                                                    showticklabels=True),
                             hovermode='closest')

        data7 = pgo.Data(trace_arr)
        layout7 = layout5
        layout7['title'] = 'Data Clusters'
        fig7 = pgo.Figure(data=data7, layout=layout7)

        # Plot model
        html_file_location = html_plots_location + model_name + ".html"
        html_path = html_short_path + model_name + ".html"
        fig = make_subplots(rows=2, cols=1)
        # 1- clusters
        for k in range(len(fig7.data)):
            fig.add_trace(fig7.data[k], row=1, col=1)
        # 2- Elbow graph
        # TODO: Add code to implent Elbow function and plot it with the clustering graph

        pl.offline.plot(fig, filename=html_file_location, config={'displayModeBar': False}, auto_open=False)

        return html_path

    @staticmethod
    def plot_elbow_graph(data, model_id, model_name='file_name'):
        data = np.reshape(data, (len(data), 1))
        mms = MinMaxScaler()
        mms.fit(data)
        data_transformed = mms.transform(data)

        Sum_of_squared_distances = []
        K = range(1, 25)
        x_axis = [*K]
        y_axis = Sum_of_squared_distances
        for k in K:
            km = KMeans(n_clusters=k)
            km = km.fit(data_transformed)
            Sum_of_squared_distances.append(km.inertia_)

        fig = pgo.Figure(
            data=[pgo.Scatter(x=x_axis, y=y_axis, line_color="crimson", marker=pgo.scatter.Marker(symbol='x',
                                                                                                  size=10,
                                                                                                  color='black'),
                              name="Elbow Graph",
                              text="Number of Clusters",
                              showlegend=True)],
            layout_title_text="A Graph of suggested number of clusters"
        )

        html_file_location = html_plots_location + model_id + '/' + model_name + ".html"
        html_path = html_short_path + model_id + '/' + model_name + ".html"
        pl.offline.plot(fig, filename=html_file_location, config={'displayModeBar': False}, auto_open=False)

        return html_path

    @staticmethod
    def plot_model_clusters(model_id, features, labels, model_name='file_name'):
        # Create a PCA object to reduce the dimensionality of the data to 2 dimensions
        pca = PCA(n_components=2)

        # Use the PCA object to transform the bag-of-words data to 2 dimensions
        X_pca = pca.fit_transform(features.toarray())

        # Create a scatterplot of the transformed data with color-coded cluster labels
        fig = pgo.Figure(data=pgo.Scatter(x=X_pca[:, 0], y=X_pca[:, 1], mode='markers', marker=dict(color=labels)))

        # Add titles to the X and Y axes
        fig.update_layout(xaxis_title="X Factors", yaxis_title="Y factors")

        html_file_location = html_plots_location + model_id + '/' + model_name + ".html"
        html_path = html_short_path + model_id + '/' + model_name + ".html"
        pl.offline.plot(fig, filename=html_file_location, config={'displayModeBar': False}, auto_open=False)

        return html_path

    @staticmethod
    def extract_clusters_keywords(model, k, vectorizer):
        """
            Extract the keywords of each cluster then save the results in pkl file
        """
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()
        cluster_keywords = {}
        number_of_keywords = int(
            config_parser.get('SystemConfigurations', 'SystemConfigurations.number_of_clustering_keywords'))
        for i in range(k):
            cluster_name = "Cluster_" + str(i)
            cluster_terms = ''
            for j in order_centroids[i, :number_of_keywords]:  # print out 10 feature terms of each cluster
                cluster_terms = cluster_terms + terms[j] + ('' if (j == number_of_keywords) else ', ')
            cluster_keywords[cluster_name] = cluster_terms

        # Save clusters' keywords in pkle file
        a_file = open(clusters_keywords_file, "wb")
        pickle.dump(cluster_keywords, a_file)
        a_file.close()

        return cluster_keywords

    @staticmethod
    def get_clustering_keywords():
        with open(clusters_keywords_file, 'rb') as f:
            loaded_clustering_keywords = pickle.load(f)

        return loaded_clustering_keywords

    @staticmethod
    def get_cluster_keywords(cluster):
        """
        Return arra of keywords of provided cluster
        @param cluster:
        @return:
        """
        clusters_keywords = ClusteringControllerHelper.get_clustering_keywords()
        cluster_keywords = clusters_keywords['Cluster_' + str(cluster)]

        return cluster_keywords

    def evaluate_clustfer(self, classifier, vectorizer, X_test, y_test, categories):
        return 0, 1, 2

    def get_clusterfer_splits(self, docs):
        shuffle(docs)
        return docs

    def create_clustering_data_set(self, files_path):
        try:
            output_file = '%s%s' % (files_path, 'data.pkl')
            files_data = {}
            if os.path.exists(output_file):
                os.remove(output_file)

            with open(output_file, 'w', encoding='utf8') as outfile:
                for filename in os.listdir(files_path):
                    with open(filename, 'rb') as file:
                        text = file.read().decode(errors='replace').replace('\n', '')
                        files_data.append(text)
                        outfile.write('%s\n' % (text))
            df = pd.DataFrame(files_data)
            df.to_pickle(outfile)

            return 1
        except  Exception as e:
            print(e)
            return 0

    def create_clustering_csv_data_set(self, model_id, csv_file_path, features_list):
        try:
            df = pd.read_csv(csv_file_path)
            df = df.loc[:, features_list]
            output_file = '%s%s%s%s%s' % (df_location, str(model_id), '/', str(model_id), '.pkl')
            df.to_pickle(output_file)

            return 1
        except  Exception as e:
            print(e)
            return 0

    def create_clustering_FTP_data_set(self, location_details):
        try:
            output_file = '%s%s' % (df_location, 'data.pkl')
            helper = Helper()
            ftp_conn = helper.create_FTP_conn(location_details)
            files_data = []

            # Reading files contents and save it in pkl file
            ftp_conn.cwd(df_location)
            files_list = ftp_conn.nlst()
            for filename in files_list:
                fullfilename = filename
                gFile = open("temp.txt", "wb")
                ftp_conn.retrbinary(f"RETR {fullfilename}", gFile.write)
                gFile.close()
                with open("temp.txt", 'rb') as file:
                    text = file.read().decode(errors='replace').replace('\n', '')
                    files_data.append(text)
                gFile.close()
            ftp_conn.quit()

            df = pd.DataFrame(files_data)
            df.to_pickle(output_file)

            return 1
        except  Exception as e:
            print(e)
            return 0

    @staticmethod
    def generate_labeled_datafile(file_name, labels: []):
        """
        Create csv file with label column from data file of unlabeled data
        @param file_name:
        @param labels:
        @return: path of updated data file
        """
        try:
            data_file_location = "%s%s%s%s%s" % (df_location, file_name, '/', file_name, '.csv')
            updated_data_file_location = "%s%s%s%s" % (output_docs_location, file_name, '/', labeled_data_filename)

            df = pd.read_csv(data_file_location)
            df['label'] = labels
            df.to_csv(updated_data_file_location, index=False)

            return updated_data_file_location
        except Exception as e:
            return Helper.display_property('ErrorMessages.fail_create_updated_data_file')

    def _calculate_no_clusters(self, df_scaled):
        # calculate k using python, with the elbow method
        inertia = []

        # define our possible k values
        possible_K_values = [i for i in range(2, 25)]

        # we start with 2, as we can not have 0 clusters in k means, and 1 cluster is just a dataset

        # iterate through each of our values
        for each_value in possible_K_values:
            # iterate through, taking each value from
            model = KMeans(n_clusters=each_value, init='k-means++', random_state=32)

            # fit it
            model.fit(df_scaled)

            # append the inertia to our array
            inertia.append(model.inertia_)

        plt.plot(possible_K_values, inertia)
        plt.title('The Elbow Method')

        plt.xlabel('Number of Clusters')

        plt.ylabel('Inertia')

        plt.show()

        # ----------------------------------------------#
        # now we have a problem, which K do we choose? anything past 15 looks really good, let's test 25

        # let's use silhouette_samples and silhouette_score to find out

        # new model
        model = KMeans(n_clusters=25, init='k-means++', random_state=32)

        # re-fit our model
        model.fit(df_scaled)

        # compute an average silhouette score for each point
        silhouette_score_average = silhouette_score(df_scaled, model.predict(df_scaled))

        # let's see what that score it
        print(silhouette_score_average)

        # 0.261149550725173

        # while that's nice, what does that tell us? there could still be a points with a negative value

        # let's see the points
        silhouette_score_individual = silhouette_samples(df_scaled, model.predict(df_scaled))

        # iterate through to find any negative values
        for each_value in silhouette_score_individual:
            if each_value < 0:
                print(f'We have found a negative silhouette score: {each_value}')

        # ----------------------------------------------#
        # re-do our loop, try to find values with no negative scores, or one with the least!!
        bad_k_values = {}

        # remember, anything past 15 looked perfect based on the inertia
        possible_K_values = [i for i in range(2, 30)]  # [i for i in range(15, 30)]

        # we start with 1, as we can not have 0 clusters in k means
        # iterate through each of our values
        for each_value in possible_K_values:

            # iterate through, taking each value from
            model = KMeans(n_clusters=each_value, init='k-means++', random_state=32)

            # fit it
            model.fit(df_scaled)

            # find each silhouette score
            silhouette_score_individual = silhouette_samples(df_scaled, model.predict(df_scaled))

            # iterate through to find any negative values
            for each_silhouette in silhouette_score_individual:

                # if we find a negative, lets start counting them
                if each_silhouette < 0:

                    if each_value not in bad_k_values:
                        bad_k_values[each_value] = 1

                    else:
                        bad_k_values[each_value] += 1

        best_key = list(bad_k_values.keys())[0]
        less_minuse_value = list(bad_k_values.values())[0]
        for key, val in bad_k_values.items():
            if val <= less_minuse_value:
                best_key = key
                less_minuse_value = val
            print(f' This Many Clusters: {key} | Number of Negative Values: {val}')
            print(f'Best number of clusters = {best_key} with {less_minuse_value} number of minus values')
        # as we can see, inertia showed us that our value needed to be bigger than 15.
        # but how did we choose past that?
        # we optimized our K value utilizing the silhouette score, choosing 16 as it has
        # the lowest amount of negative values

        return best_key

    def calculate_no_clusters(self, df_scaled):
        # Calculate the rate of change in inertia for different numbers of clusters
        silhouette_scores = []
        calinski_scores = []

        for k in range(2, 10):
            kmeans = KMeans(n_clusters=k)
            kmeans.fit(df_scaled)
            labels = kmeans.labels_
            silhouette_scores.append(silhouette_score(df_scaled, labels))
            calinski_scores.append(calinski_harabasz_score(df_scaled, labels))

        optimal_k_silhouette = np.argmax(silhouette_scores) + 2
        optimal_k_calinski = np.argmax(calinski_scores) + 2
        print("Optimal number of clusters (silhouette score):", optimal_k_silhouette)
        print("Optimal number of clusters (calinski-harabasz score):", optimal_k_calinski)

        optimal_k = optimal_k_silhouette #optimal_k_silhouette if optimal_k_silhouette >= optimal_k_calinski else optimal_k_calinski

        return optimal_k

    ##-------------- Recommendations Functions -------------##

    def convert_to_list(slef, data):
        a = data.replace("-", "").replace("[", "").replace("]", "")
        #     a = ''.join([i for i in a if not i.isdigit()])
        a = a.translate(str.maketrans('', '', string.punctuation))
        return a

    def _train_recommendation_model(self):
        return 0

    def _preparedata(self):
        try:
            a = pd.read_csv("input/RAW_interactions.csv")
            a.head(2)

            b = pd.read_csv("input/RAW_recipes.csv")
            b.head(3)

            # Data set is big so take some random samples
            a = a.sample(50000)
            b = b.sample(50000)

            data = pd.merge(a, b, right_on='id', left_on='recipe_id')
            data.drop(["user_id", "submitted", "contributor_id", "id"], axis=1, inplace=True)

            data[['calories', 'total fat', 'sugar', 'sodium', 'protein', 'saturated fat',
                  'carbohydrates']] = data.nutrition.str.split(",", expand=True)
            data['calories'] = data['calories'].apply(lambda x: x.replace("[", ""))
            data['carbohydrates'] = data['carbohydrates'].apply(lambda x: x.replace("]", ""))
            data[['calories', 'total fat', 'sugar', 'sodium', 'protein', 'saturated fat', 'carbohydrates']] = data[
                ['calories', 'total fat', 'sugar', 'sodium', 'protein', 'saturated fat', 'carbohydrates']].astype(float)

            fig, ax = plt.subplots(1, 2, figsize=(15, 4))
            sns.distplot(data["minutes"], ax=ax[0])
            sns.distplot(data["n_steps"], ax=ax[1])

            fig, ax = plt.subplots(1, 2, figsize=(15, 4))
            sns.boxplot(data=data["minutes"], ax=ax[0])
            sns.boxplot(data=data["n_steps"], ax=ax[1])

            q1 = np.percentile(data["minutes"], 25)
            q3 = np.percentile(data["minutes"], 75)
            IQR = q3 - q1
            upper = q3 + 1.5 * IQR
            lower = q1 - 1.5 * IQR

            qq = data[data["minutes"] >= upper].index
            ee = data[data["minutes"] <= lower].index
            data = data.drop(data[data["minutes"] >= upper].index, axis=0)
            data = data.drop(data[data["minutes"] <= lower].index, axis=0)

            q1 = np.percentile(data["n_steps"], 25)
            q3 = np.percentile(data["n_steps"], 75)
            IQR = q3 - q1
            upper = q3 + 1.5 * IQR
            lower = q1 - 1.5 * IQR

            data = data.drop(data[data["n_steps"] >= upper].index, axis=0)
            data = data.drop(data[data["n_steps"] <= lower].index, axis=0)

            data.isnull().sum()
            data.dropna(inplace=True)

            nonveg_ingred = ["egg", "egg whites", ]

            def ingredient_check(data):
                veg = 0
                for a in literal_eval(data):
                    if a in nonveg_ingred:
                        veg = 1
                    else:
                        veg = 0
                return veg

            data["non veg"] = data["ingredients"].apply(ingredient_check)

            rec = data[["recipe_id", "rating", "name", "tags", "description", "ingredients", ]]

            rate = rec.groupby("name")["rating"].sum().reset_index()

            rec.duplicated().sum()
            rec.drop_duplicates(inplace=True)

            rec.reset_index(drop=True, inplace=True)

            rec.head(2)

            rec["tags"] = rec["tags"].apply(lambda x: self.convert_to_list(x))
            rec["ingredients"] = rec["ingredients"].apply(lambda x: self.convert_to_list(x))
            rec["description"] = rec["description"].apply(lambda x: self.convert_to_list(x))

            rec["rec"] = rec["tags"] + rec["description"] + rec["ingredients"]
            rec = rec[~rec.duplicated("name")]
            rec.reset_index(drop=True, inplace=True)

            rec.to_csv("food.csv")

            cv = TfidfVectorizer()
            rec_tfidf = cv.fit_transform(rec["rec"])
            name_tfidf = cv.fit_transform(rec["name"])
            rec_consin_sim = linear_kernel(rec_tfidf, rec_tfidf)
            name_consin_sim = linear_kernel(name_tfidf, name_tfidf)
            indices = pd.Series(rec.index, index=rec['name'])

            # Save model
            pickle.dump(rec, open('pkls/rec.pkl', 'wb'))
            pickle.dump(rec_consin_sim, open('pkls/rec_consin_sim.pkl', 'wb'))
            pickle.dump(name_consin_sim, open('pkls/name_consin_sim.pkl', 'wb'))
            pickle.dump(indices, open('pkls/indices.pkl', 'wb'))

            return "Sucess"
        except Exception as e:
            print(e)
            return "Fail"

    def recommendation(self, desc):
        rec_array = [["recipe_id", "rating", desc, "tags", "description", "ingredients"]]
        data = pd.DataFrame(rec_array, columns=["recipe_id", "rating", "name", "tags", "description", "ingredients"])

        # load pkls
        rec = pickle.load(open('pkls/rec.pkl', 'rb'))
        sim = pickle.load(open('pkls/rec_consin_sim.pkl', 'rb'))
        indices = pickle.load(open('pkls/indices.pkl', 'rb'))

        re_li = []
        ind = indices[data['name']]
        sim_score = list(enumerate(sim[ind]))
        sim_score = sorted(sim_score, key=lambda x: x[1], reverse=True)
        sim_score = sim_score[0:10]
        rec_indices = [i[0] for i in sim_score]
        for i in rec_indices:
            re_li.append(rec.iloc[i]["name"])
        return re_li

    ##-------------- End Recommendations Functions -------------##
