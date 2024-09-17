import pandas as pd
import re
from dateutil import parser
import logging

## FUNCION EDAD

def string_to_number(file_path, column):
    """
    Convert a specified column in a CSV file to float and save the updated DataFrame back to the same file.

    Parameters:
    file_path (str): Path to the CSV file.
    column (str): Name of the column to convert.
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path, sep=';')

        # Convert the specified column to float
        df[column] = df[column].astype(float)

        # Save the updated DataFrame back to the same file
        df.to_csv(file_path, sep=';', index=False)

        print(f"Successfully converted column '{column}' to float and saved to {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")


def add_days_passed_column(df, datetime_column, new_column_name):
    """
    Add a new column to the DataFrame that counts the number of days passed since the date in the datetime_column.
    """
    # Ensure the datetime_column is in datetime format
    df[datetime_column] = pd.to_datetime(df[datetime_column], errors='coerce')

    # Calculate the number of days passed
    current_date = pd.Timestamp.now()
    df[new_column_name] = (current_date - df[datetime_column]).dt.days

    return df


def Checking_IDS(data, report_dto, added_sections):
    """
    Identify columns with all different values (possible IDs) and add them to the report.

    Parameters:
    - data: DataFrame containing the dataset.
    - report_dto: ReportDTO object to which the IDs list will be added.
    - added_sections: List to keep track of added sections in the report.

    Returns:
    - ids_columns: List of columns identified as possible IDs.
    """
    try:
        # Identify Columns with All Different Values and Create "IDs" List
        ids_columns = []
        for column in data.columns:
            if data[column].nunique() >= 0.94 * len(data):
                ids_columns.append(column)

        # Add "IDs" List to Report
        ids_list = ', '.join(ids_columns)
        report_dto.add_section("Possible IDs", ids_list)
        added_sections.append("Possible IDs")

        logging.info("Possible IDs section added successfully.")
        return ids_columns

    except Exception as e:
        logging.error(f"Failed to identify columns with all different values: {e}")
        return []

power_mapping = {
    range(17, 21): '18-20',
    range(21, 26): '21-25',
    range(26, 31): '26-30',
    range(31, 36): '31-35',
    range(36, 41): '36-40',
    range(41, 46): '41-45',
    range(46, 51): '46-50',
    range(51, 100): '+50'
}

def map_age_to_range(age):
    for age_range, age_label in power_mapping.items():
        if age in age_range:
            return age_label


def add_years_passed_column(df, datetime_column, new_column_name):
    """
    Add a new column to the DataFrame that counts the number of years passed since the date in the datetime_column.
    """
    # Ensure the datetime_column is in datetime format
    df[datetime_column] = pd.to_datetime(df[datetime_column], errors='coerce')

    # Calculate the number of years passed
    current_date = pd.Timestamp.now()
    df[new_column_name] = (current_date - df[datetime_column]).astype('<m8[Y]').astype(int)

    return df


def datetime_to_year(df, column):
    # Extract the year from the datetime column
    df[column] = pd.to_datetime(df[column]).dt.year

    # Convert the column to integer
    df[column] = df[column].astype(int)

    # Save the DataFrame back to the CSV file
    csv_path = df.to_csv(index=False)
    df.to_csv(csv_path, index=False)

    return df


def save_df_to_csv(df, file_path):
    """
    Save the DataFrame to a CSV file.

    Parameters:
    df (pd.DataFrame): The DataFrame to be saved.
    file_path (str): The path where the CSV file will be saved.
    """
    df.to_csv(file_path, index=False)


# Utility functions
def convert_str_to_float(df):
    converted_columns = []

    def clean_string(x):
        """
        Clean the monetary string to ensure proper float conversion.
        Remove currency symbols and commas, and retain only the last decimal point.
        """
        if isinstance(x, str):
            # Remove currency symbols and spaces
            x = re.sub(r'[^\d,.-]', '', x).replace(' ', '')

            # Replace commas with dots
            x = x.replace(',', '.')

            # Retain only the last decimal point
            parts = x.split('.')
            if len(parts) > 2:
                x = ''.join(parts[:-1]) + '.' + parts[-1]
        return x

    def is_numeric_string(x):
        """
        Check if the cleaned string is numeric.
        """
        x_cleaned = clean_string(x)
        return pd.isna(x) or x_cleaned.replace('.', '', 1).isdigit()

    for column in df.select_dtypes(include='object').columns:
        if not column.startswith("FLAG"):
            # Check if the column contains values that are numeric when represented as strings, excluding NaNs
            is_numeric_column = df[column].apply(is_numeric_string).all()
            if is_numeric_column:
                try:
                    # Convert the cleaned column to float
                    df[column] = pd.to_numeric(df[column].apply(clean_string), errors='coerce')
                    converted_columns.append(column)
                except ValueError as e:
                    logging.error(f"Error converting column {column} to float: {e}")

    return df, converted_columns
def convert_str_to_datetime(df):
    converted_columns = []
    date_patterns = [
        re.compile(r'^\d{4}/\d{1,2}/\d{1,2}$'),          # Pattern for 'YYYY/MM/DD'
        re.compile(r'^\d{1,2}/\d{1,2}/\d{4}$'),          # Pattern for 'DD/MM/YYYY' or 'MM/DD/YYYY'
        re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'),          # Pattern for 'YYYY-MM-DD'
        re.compile(r'^\d{1,2}-\d{1,2}-\d{4}$'),          # Pattern for 'DD-MM-YYYY'
        re.compile(r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$'),  # Pattern for 'YYYY/MM/DD HH:MM'
        re.compile(r'^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$'),  # Pattern for 'DD/MM/YYYY HH:MM' or 'MM/DD/YYYY HH:MM'
        re.compile(r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}$'),  # Pattern for 'YYYY-MM-DD HH:MM'
        re.compile(r'^\d{1,2}-\d{1,2}-\d{4} \d{1,2}:\d{2}$')   # Pattern for 'DD-MM-YYYY HH:MM'
    ]

    def clean_date_string(date_str):
        return date_str.replace(' 00:00', '')

    for column in df.select_dtypes(include='object').columns:
        if not df[column].dropna().empty:
            sample_value = df[column].dropna().astype(str).iloc[0]
            cleaned_sample_value = clean_date_string(sample_value)
            if any(pattern.match(cleaned_sample_value) for pattern in date_patterns):
                try:
                    # Clean spaces in the entire column
                    df[column] = df[column].apply(lambda x: clean_date_string(x) if pd.notna(x) else x)
                    # Try parsing date with dateutil parser
                    # df[column] = df[column].apply(lambda x: parser.parse(x, dayfirst=True) if pd.notna(x) else x)
                    converted_columns.append(column)
                except Exception as e:
                    print(f"Error parsing column {column}: {e}")
                    pass
    return df, converted_columns


def is_ambiguous_date(date_str):
    try:
        parts = date_str.split('-')
        if len(parts) == 3:
            year, month, day = parts
            if int(month) <= 12 and int(day) <= 12:
                return True
        parts = date_str.split('/')
        if len(parts) == 3:
            year, month, day = parts
            if int(month) <= 12 and int(day) <= 12:
                return True
    except Exception:
        pass
    return False
def convert_to_bool(df):
    converted_columns = []

    for column in df.columns:
        # Drop NA values and get unique values
        unique_values = df[column].dropna().unique()

        # Check if the column has 2 unique values and if those values are numeric (0 and 1)
        if len(unique_values) == 2 and all(pd.api.types.is_numeric_dtype(type(value)) for value in unique_values):
            try:
                # Check if unique values are 0 and 1
                if set(unique_values) == {0, 1}:
                    df[column] = df[column].astype(bool)
                    converted_columns.append(column)
            except ValueError as e:
                logging.error(f"Error converting column {column} to bool: {e}")

    return df, converted_columns