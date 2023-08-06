import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.python.keras.models import load_model
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

    def predictlabels(self, model_id, features):
        try:
            model_path = "{}{}".format(pkls_location, model_id)
            model = load_model(model_path)
            labels = model.predict(features)

            return labels
        except Exception as e:
            print(e)
            return None

    def _calculate_permutation_importance_multiclass(self, model, X, y, loss_func):
        """
        Calculate and display permutation importance for multiclass classification
        @param model:
        @param X:
        @param y:
        @param loss_func:
        @return:
        """
        baseline_loss = loss_func(y, model.predict(X)).numpy()
        importances = []

        for feature in range(X.shape[1]):
            X_permuted = X.copy()
            X_permuted[:, feature] = np.random.permutation(X[:, feature])
            permuted_loss = loss_func(y, model.predict(X_permuted)).numpy()
            importances.append(baseline_loss - permuted_loss)

        return np.array(importances)

    def _calculate_permutation_importance_multilabel(self, model, X, y, loss_func):
        """
        Calculate and display permutation importance for multilabel classification
        @param model:
        @param X:
        @param y:
        @param loss_func:
        @return:
        """
        baseline_loss = loss_func(y, model.predict(X)).numpy()
        importances = []

        for feature in range(X.shape[1]):
            X_permuted = X.copy()
            X_permuted[:, feature] = np.random.permutation(X[:, feature])
            permuted_loss = loss_func(y, model.predict(X_permuted)).numpy()
            importances.append(baseline_loss - permuted_loss)

        return np.array(importances)

    # Class for calcualting the improtance of each label however it is multiclass label or multilabel label
    class dummy:
        import numpy as np
        import tensorflow as tf
        from sklearn.model_selection import train_test_split
        from tensorflow.python.keras.losses import sparse_categorical_crossentropy, binary_crossentropy

        # Generate a synthetic dataset
        np.random.seed(42)
        n_samples = 1000
        n_features = 5
        n_classes = 3

        X = np.random.randn(n_samples, n_features)
        # y contains multiclass labels (e.g., 0, 1, 2) for the first half and multilabel data (binary values) for the second half
        y_multiclass = np.random.randint(0, n_classes, size=n_samples // 2)
        y_multilabel = np.random.randint(0, 2, size=(n_samples - n_samples // 2, n_classes))

        y = np.concatenate((y_multiclass, y_multilabel), axis=0)

        # Split the data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create a simple TensorFlow model for multiclass classification
        model_multiclass = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(n_features,)),
            tf.keras.layers.Dense(n_classes, activation='softmax')
        ])

        # Compile the model for multiclass classification
        model_multiclass.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train the model for multiclass classification
        model_multiclass.fit(X_train, y_train[:n_samples // 2], epochs=10, batch_size=32, verbose=0)

        # Create a simple TensorFlow model for multilabel classification
        model_multilabel = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(n_features,)),
            tf.keras.layers.Dense(n_classes, activation='sigmoid')
        ])

        # Compile the model for multilabel classification
        model_multilabel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # Train the model for multilabel classification
        model_multilabel.fit(X_train, y_train[n_samples // 2:], epochs=10, batch_size=32, verbose=0)

        # Calculate and display permutation importance for multiclass classification
        def calculate_permutation_importance_multiclass(model, X, y, loss_func):
            baseline_loss = loss_func(y, model.predict(X)).numpy()
            importances = []

            for feature in range(X.shape[1]):
                X_permuted = X.copy()
                X_permuted[:, feature] = np.random.permutation(X[:, feature])
                permuted_loss = loss_func(y, model.predict(X_permuted)).numpy()
                importances.append(baseline_loss - permuted_loss)

            return np.array(importances)

        perm_importances_multiclass = calculate_permutation_importance_multiclass(model_multiclass, X_test,
                                                                                  y_test[:n_samples // 2],
                                                                                  sparse_categorical_crossentropy)

        # Calculate and display permutation importance for multilabel classification
        def calculate_permutation_importance_multilabel(model, X, y, loss_func):
            baseline_loss = loss_func(y, model.predict(X)).numpy()
            importances = []

            for feature in range(X.shape[1]):
                X_permuted = X.copy()
                X_permuted[:, feature] = np.random.permutation(X[:, feature])
                permuted_loss = loss_func(y, model.predict(X_permuted)).numpy()
                importances.append(baseline_loss - permuted_loss)

            return np.array(importances)

        perm_importances_multilabel = calculate_permutation_importance_multilabel(model_multilabel, X_test,
                                                                                  y_test[n_samples // 2:],
                                                                                  binary_crossentropy)

        # Display feature importances for multiclass classification
        feature_names = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5']
        print("Permutation Importance for Multiclass Classification:")
        for feature, importance in zip(feature_names, perm_importances_multiclass):
            print(f"{feature}: {importance:.4f}")

        # Display feature importances for multilabel classification
        print("\nPermutation Importance for Multilabel Classification:")
        for feature, importance in zip(feature_names, perm_importances_multilabel):
            print(f"{feature}: {importance:.4f}")


