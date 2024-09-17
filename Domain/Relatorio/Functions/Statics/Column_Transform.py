import logging
from io import StringIO
from .data_process import convert_str_to_datetime, convert_to_bool, convert_str_to_float

def split_text_into_lines(text, max_length=80):
    words = text.split(', ')
    lines = []
    current_line = []

    for word in words:
        if len(', '.join(current_line + [word])) > max_length:
            lines.append(', '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)

    if current_line:
        lines.append(', '.join(current_line))

    return lines

def Data_info_and_transform(data, report_dto, added_sections, table=None):
    """
    Processes and transforms the data, and adds relevant sections to the report.

    Parameters:
    - data: DataFrame containing the dataset.
    - report_dto: ReportDTO object to which the sections will be added.
    - added_sections: List to keep track of added sections in the report.
    - table: Optional name of the table to include in the report intro.

    Returns:
    - data: Transformed DataFrame.
    - int_columns, float_columns, str_columns, bool_columns: Lists of columns by data type.
    """
    try:
        # Introductory Text
        columns = data.columns.tolist()
        col_string = ', '.join(columns)
        col_string_lines = split_text_into_lines(col_string, max_length=80)

        # Calculate the number of rows, columns, and total amount of data
        num_rows = len(data)
        num_columns = len(data.columns)
        total_data_points = num_rows * num_columns

        # Add the introductory text with additional information
        intro = (
            f"The dataset contains {num_rows} rows, {num_columns} columns, "
            f"and a total of {total_data_points} data points"
        )
        if table:
            intro += f" in {table}."

        intro += "\nThe columns are:\n" + '\n'.join(col_string_lines)

        report_dto.add_section("Introduction", intro)
        added_sections.append("Introduction")
        logging.info("Introduction section added.")
    except Exception as e:
        logging.error(f"Failed to add introduction section: {e}")

    try:
        # Capture Column Info before transformation
        buffer = StringIO()
        data.info(buf=buffer)
        col_info = buffer.getvalue()
        report_dto.add_section("Column Info", col_info)
        added_sections.append("Column Info")
        logging.info("Column Info section added.")
    except Exception as e:
        logging.error(f"Failed to add column info section: {e}")

    try:
        # Convert string columns to datetime where applicable
        data, datetime_converted_columns = convert_str_to_datetime(data)
        # Convert columns to bool where applicable
        data, bool_converted_columns = convert_to_bool(data)
        # Convert string columns to int where applicable
        data, int_converted_columns = convert_str_to_float(data)
    except Exception as e:
        logging.error(f"Failed to convert columns: {e}")

    try:
        # Capture Column Info after transformation
        buffer = StringIO()
        data.info(buf=buffer)
        col_info_transformed = buffer.getvalue()
        report_dto.add_section("Column Info Transformed", col_info_transformed)
        added_sections.append("Column Info Transformed")
        logging.info("Column Info Transformed section added.")
    except Exception as e:
        logging.error(f"Failed to add transformed column info section: {e}")

    try:
        # Add transformed columns to the report
        transformed_columns = (
            f"Converted to datetime: {', '.join(datetime_converted_columns)}\n"
            f"\nConverted to int: {', '.join(int_converted_columns)}\n"
            f"\nConverted to bool: {', '.join(bool_converted_columns)}\n"
        )
        col_string_lines_transformed = split_text_into_lines(transformed_columns, max_length=80)
        report_dto.add_section("Transformed Columns", '\n'.join(col_string_lines_transformed))
        added_sections.append("Transformed Columns")
        logging.info("Transformed Columns section added.")
    except Exception as e:
        logging.error(f"Failed to add transformed columns section: {e}")

    try:
        # Separate columns by data type
        int_columns = data.select_dtypes(include='int').columns.tolist()
        float_columns = data.select_dtypes(include='float').columns.tolist()
        str_columns = data.select_dtypes(include='object').columns.tolist()
        bool_columns = data.select_dtypes(include='bool').columns.tolist()

        int_columns_lines = split_text_into_lines(', '.join(int_columns), max_length=80)
        float_columns_lines = split_text_into_lines(', '.join(float_columns), max_length=80)
        str_columns_lines = split_text_into_lines(', '.join(str_columns), max_length=80)

        report_dto.add_section("Integer Columns", '\n'.join(int_columns_lines))
        report_dto.add_section("Float Columns", '\n'.join(float_columns_lines))
        report_dto.add_section("String Columns", '\n'.join(str_columns_lines))
        report_dto.add_section("Boolean Columns", '\n'.join(bool_columns))
        added_sections.extend(["Integer Columns", "Float Columns", "String Columns", "Boolean Columns"])
        logging.info("Data type sections added.")
    except Exception as e:
        logging.error(f"Failed to add data type sections: {e}")

    return data, int_columns, float_columns, str_columns, bool_columns
