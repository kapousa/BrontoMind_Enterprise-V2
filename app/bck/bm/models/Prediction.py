import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.models import load_model
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
            optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
            model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

            # Add an early stopping callback.
            early_stopping = tf.keras.callbacks.EarlyStopping(patience=10)

            target_accuracy = 0.95
            current_accuracy = 0.0
            retrain_count = 0


            # Train the model
            model.fit(x_train, y_train, epochs=200, batch_size=32, callbacks=[early_stopping])

            # Evaluate the model
            loss, current_accuracy = model.evaluate(x_train, y_train, verbose=0)
            print(f"Iteration {retrain_count + 1}: Accuracy = {current_accuracy:.4f}")
            accuracy = round(100 * current_accuracy, 2)  # model.evaluate(X_train, y_train)[0] is the loss value (same like SME)

            # Saving and reloading
            model.save(save_model_path)

            # Predict the labels for the test data
            y_pred = model.predict(x_test)

            return model, y_pred, accuracy, 3

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
