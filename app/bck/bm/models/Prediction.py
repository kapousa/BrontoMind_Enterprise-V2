import numpy as np
import pandas as pd
from keras.layers import Input
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, average_precision_score, precision_recall_curve
from sklearn.metrics import  f1_score
import tensorflow as tf
from tensorflow.python.keras.layers import Dense, Layer
from tensorflow.python.keras.models import load_model, Model
from keras.models import Sequential
from app.constants.BM_CONSTANTS import pkls_location


class Prediction:

    def _createmodel(self, model_id, df, features, labels):
        """
        Create prediction model
        @param model_id: model Id
        @param df: DataFrame
        @param features: Model Features
        @param labels: Model Labels
        @return: Model Accuracy Score
        """
        try:
            save_model_path = "{}{}".format(pkls_location, model_id)
            X = pd.get_dummies(df.drop(labels, axis=1))
            y = pd.get_dummies(df.drop(features, axis=1))
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
            y_train.head()
            X_train = X_train.astype(float)
            y_train = y_train.astype(float)

            # Build the model
            model = Sequential()
            model.add(Dense(units=32, activation='relu', input_dim=len(X_train.columns)))
            model.add(Dense(units=64, activation='relu'))
            model.add(Dense(units=1, activation='sigmoid'))
            model.compile(loss='binary_crossentropy', optimizer='sgd', metrics='accuracy')

            # Fit, predict, and evaluate
            model.fit(X_train, y_train, epochs=200, batch_size=32, classes=len(labels))

            y_pred = model.predict(X_test)
            accuracy_score(y_test, y_pred)

            # Saving and reloading
            model.save(save_model_path)

            # del model
            # model = load_model(f"{SAVE_MODEL}tfmodel")
            return model, y_pred, accuracy_score, 11

        except Exception as e:
            print(e)
            return -1

    def c_reatemodel(self, model_id, df, features, labels):
        """
            Create prediction model
            @param model_id: model Id
            @param df: DataFrame
            @param features: Model Features
            @param labels: Model Labels
            @return: Model Accuracy Score
            """
        try:
            save_model_path = "{}{}".format(pkls_location, model_id)
            X = pd.get_dummies(df.drop(labels, axis=1))
            y = pd.get_dummies(df.drop(features, axis=1))
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
            y_train.head()
            X_train = X_train.astype(float)
            y_train = y_train.astype(float)

            # Create a model with two output layers
            model = tf.keras.models.Sequential([
                tf.keras.layers.Dense(units=32, activation='relu', input_dim=len(X_train.columns)),
                tf.keras.layers.Dense(units=16, activation='relu'),
                tf.keras.layers.Dense(units=2, activation='softmax')
            ])

            # Compile the model
            model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

            # Fit the model
            model.fit(X_train, y_train, epochs=200, batch_size=32)

            y_pred = model.predict(X_test)

            # Calculate the precision and recall curves
            precision, recall, thresholds = precision_recall_curve(y_test, y_pred)

            # Calculate the average precision score
            ap = np.mean(2 * precision * recall / (precision + recall))

            # Saving and reloading
            model.save(save_model_path)

            # del model
            # model = load_model(f"{SAVE_MODEL}tfmodel")
            return model, y_pred, ap, 11

        except Exception as e:
            print(e)
            return -1

    def createmodel(self, model_id, df, features, labels):
        """
        Create prediction model
        @param model_id: model Id
        @param df: DataFrame
        @param features: Model Features
        @param labels: Model Labels
        @return: Model Accuracy Score
        """
        try:
            save_model_path = "{}{}".format(pkls_location, model_id)
            X = pd.get_dummies(df.drop(labels, axis=1))
            y = pd.get_dummies(df.drop(features, axis=1))
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
            y_train.head()
            X_train = X_train.astype(float)
            y_train = y_train.astype(float)

            # Create the model
            model = tf.keras.Sequential([
                tf.keras.layers.Flatten(input_shape=(len(features),)),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dense(2, activation='softmax')
            ])

            # Compile the model
            model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

            # Train the model
            model.fit(X_train, y_train, epochs=200, batch_size=32)

            # Evaluate the model
            accuracy = round(100 * model.evaluate(X_train, y_train)[1], 2) # model.evaluate(X_train, y_train)[0] is the loss value (same like SME)

            # Saving and reloading
            model.save(save_model_path)

            # Predict the labels for the test data
            y_pred = model.predict(X_test)

            return model, y_pred, accuracy, 7

        except Exception as e:
            print(e)
            return -1

    def predictlabels(self, model_id, features):
        try:
            model_path = "{}{}".format(pkls_location, model_id)
            model = load_model(model_path)
            labels = model.predict(features)

            return labels
        except Exception as e:
            print(e)
            return None

    # Custom layer to handle intermediate operations
    class CustomLayer(Layer):
        def call(self, inputs):
            # Perform the intermediate operation here
            return tf.math.add(inputs, 0)  # Replace this with the actual operation

