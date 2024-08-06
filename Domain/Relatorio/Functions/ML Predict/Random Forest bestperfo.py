import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import TruncatedSVD
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import joblib  # For saving the model

def RandomForestModel(df, numeric_columns, categorical_columns, variable_objetivo):
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

    # TruncatedSVD for dimensionality reduction
    n_components = 20  # Adjust based on your needs
    svd = TruncatedSVD(n_components=n_components)
    X_reduced = svd.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=0.3, random_state=42)

    # Define the parameter grid with max_features='sqrt'
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_features': ['sqrt', 'log2'],  # Replace 'auto' with 'sqrt'
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    # Create the GridSearchCV object
    grid_search = GridSearchCV(estimator=RandomForestClassifier(random_state=42),
                               param_grid=param_grid,
                               cv=5,
                               n_jobs=-1,
                               verbose=2)

    # Fit the grid search to the data
    grid_search.fit(X_train, y_train)

    # Print the best parameters and best score
    best_params = grid_search.best_params_
    print("Best Parameters: ", best_params)
    print("Best Cross-validation Score: ", grid_search.best_score_)

    # Use the best parameters and add class weights
    best_params['class_weight'] = 'balanced'

    # Create the Random Forest model with the best parameters and class weights
    best_model = RandomForestClassifier(**best_params, random_state=42)

    # Fit the model with class weights
    best_model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)

    return accuracy, best_model, matrix, report


def save_model(model, file_name):
    joblib.dump(model, file_name)
    print(f"Model saved to {file_name}")
