import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.models import Sequential

from app.constants.Paths import SAVE_MODEL


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
            save_model_path = "{}{}".format(SAVE_MODEL,model_id)
            X = pd.get_dummies(df.drop(features, axis=1))
            y = pd.get_dummies(df.drop(labels, axis=1))
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
            y_train.head()

            # Build the model
            model = Sequential()
            model.add(Dense(units=32, activation='relu', input_dim=len(X_train.columns)))
            model.add(Dense(units=64, activation='relu'))
            model.add(Dense(units=1, activation='sigmoid'))
            model.compile(loss='binary_crossentropy', optimizer='sgd', metrics='accuracy')

            # Fit, predict, and evaluate
            model.fit(X_train, y_train, epochs=200, batch_size=32)

            y_hat = model.predict(X_test)
            y_hat = [0 if val < 0.5 else 1 for val in y_hat]
            accuracy_score(y_test, y_hat)

            # Saving and reloading
            model.save(save_model_path)

            #del model
            #model = load_model(f"{SAVE_MODEL}tfmodel")
            return accuracy_score
        except Exception as e:
            print(e)
            return -1

    def predict(self, features):
        try:
            return ""
        except Exception as e:
            print(e)
            return None

