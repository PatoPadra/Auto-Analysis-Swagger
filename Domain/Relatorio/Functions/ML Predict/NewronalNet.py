import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import tensorflow as tf
from tensorflow import keras
from keras_tuner import RandomSearch

def build_model(hp):
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(input_shape=(20,)))  # Adjust input shape based on your features after PCA

    # Tune the number of units in the first Dense layer
    hp_units = hp.Int('units', min_value=32, max_value=512, step=32)
    model.add(keras.layers.Dense(units=hp_units, activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Dropout(rate=0.2))

    # Tune the number of hidden layers
    for i in range(hp.Int('num_layers', 1, 3)):
        model.add(keras.layers.Dense(units=hp.Int(f'layer_{i}_units', min_value=32, max_value=512, step=32),
                                     activation='relu'))
        model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Dropout(rate=0.2))

    model.add(keras.layers.Dense(1, activation='sigmoid'))

    # Tune the learning rate for the optimizer
    hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])

    model.compile(optimizer=keras.optimizers.Adam(learning_rate=hp_learning_rate),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model

def NeuralNetworkModel(df, numeric_columns, categorical_columns, variable_objetivo):
    # Create preprocessing pipelines for both numeric and categorical data
    numeric_preprocessing = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_preprocessing = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_preprocessing, numeric_columns),
            ('cat', categorical_preprocessing, categorical_columns)
        ])

    # Apply preprocessing to the training data
    X = preprocessor.fit_transform(df.drop(columns=[variable_objetivo]))
    y = df[variable_objetivo]

    # Principal Component Analysis (PCA) for dimensionality reduction
    n_components = 20  # Adjust based on your needs
    pca = PCA(n_components=n_components)
    X_reduced = pca.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=0.3, random_state=42)

    # Hyperparameter tuning using Keras Tuner
    tuner = RandomSearch(
        build_model,
        objective='val_accuracy',
        max_trials=10,
        executions_per_trial=1,
        directory='my_dir',
        project_name='NeuralNetwork')

    tuner.search(X_train, y_train, epochs=50, validation_split=0.2, callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)], verbose=2)

    best_model = tuner.get_best_models(num_models=1)[0]

    # Evaluate the best model
    y_pred = (best_model.predict(X_test) > 0.5).astype("int32")
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)

    return accuracy, best_model, matrix, report

def save_model(model, file_name):
    model.save(file_name)
    print(f"Model saved to {file_name}")
