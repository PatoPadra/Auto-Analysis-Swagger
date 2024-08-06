import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import TruncatedSVD
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import joblib  # For saving the model

def LogisticRegresion(df, numeric_columns, categorical_columns, variable_objetivo):

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

    X = preprocessor.fit_transform(df.drop(columns=[variable_objetivo]))
    y = df[variable_objetivo]

    # TruncatedSVD for dimensionality reduction
    n_components = 20  # Adjust based on your needs
    svd = TruncatedSVD(n_components=n_components)
    X_reduced = svd.fit_transform(X)

    # Train and evaluate the logistic regression model
    X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=0.3, random_state=42)
    model = LogisticRegression(max_iter=1000, solver='lbfgs')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)

    return accuracy, model, matrix, report

def save_model(model, file_name):
    joblib.dump(model, file_name)
    print(f"Model saved to {file_name}")

# Example of usage:
# accuracy, trained_model, conf_matrix, class_report = LogisticRegresion(df, numeric_columns, categorical_columns, 'target_variable')
# if accuracy > 0.8:  # Example condition for saving the model
#     save_model(trained_model, 'logistic_regression_model.pkl')
