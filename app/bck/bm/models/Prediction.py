import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.layers import Dense
from keras.models import load_model, Sequential
from app.constants.BM_CONSTANTS import pkls_location

class Prediction:

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
            x = pd.get_dummies(df.drop(labels, axis=1))
            y = pd.get_dummies(df.drop(features, axis=1))
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2)
            y_train.head()
            x_train = x_train.astype(float)
            y_train = y_train.astype(float)

            # Create the model
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(units=32, activation="relu", input_dim=len(features)),
                tf.keras.layers.Dense(units=64, activation='relu'),
                tf.keras.layers.Dense(units=len(labels), activation='sigmoid')
            ])

            # Compile the model
            model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

            # Train the model
            model.fit(x_train, y_train, epochs=200, batch_size=32)

            # Evaluate the model
            accuracy = round(100 * model.evaluate(x_train, y_train)[1],
                             2)  # model.evaluate(X_train, y_train)[0] is the loss value (same like SME)

            # Saving and reloading
            model.save(save_model_path)

            # Predict the labels for the test data
            y_pred = model.predict(x_test)

            return model, y_pred, accuracy, 3

        except Exception as e:
            print(e)
            return -1

    def _createmodel(self, model_id, df, features, labels):
        try:
            # Create some sample data
            num_rows = len(df)  # Using len() to get the number of rows
            input_shape = len(features)
            output_shape = len(labels)
            dataset = tf.data.Dataset.from_tensor_slices((df.iloc[:, :input_shape], df.iloc[:, input_shape:]))

            # Split the dataset into a training set and a test set.
            train_dataset = dataset.take(num_rows)
            test_dataset = dataset.skip(num_rows)

            # Create a sequential model with one or more Dense layers.
            model = tf.keras.Sequential([
                tf.keras.layers.Reshape((input_shape,1)),
                tf.keras.layers.Dense(10, activation='relu'),
                tf.keras.layers.Dense(output_shape)
            ])

            # Compile the model with a loss function and an optimizer.
            model.compile(loss='mse', optimizer='adam')

            # Train the model on the training set.
            model.fit(train_dataset, epochs=10)

            # Evaluate the model on the test set.
            model.evaluate(test_dataset)

            # Make predictions using the trained model
            predictions = model.predict(test_dataset)

            # Now 'predictions' contains the predicted values for your input data
            print(predictions)
            return model, predictions, 1, 3
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


