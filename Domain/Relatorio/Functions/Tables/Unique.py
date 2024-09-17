# Functions/Tables/unique_values_table.py

import logging
from ....PDFGenerator import make_table , make_split_table

def make_unique_values_table(data, report_dto, added_sections):
    unique_values_data = [[col, data[col].nunique()] for col in data.columns]
    unique_values_headers = ['Column Name', 'Unique Values Count']
    unique_values_column_widths = [440, 120]  # Adjust as needed

    # Generate tables, splitting if necessary
    tables = make_split_table(unique_values_data, unique_values_headers, unique_values_column_widths)

    # Add each table to the report
    for i, table in enumerate(tables):
        section_name = f"Table_Unique Values Count (Part {i+1})"
        report_dto.add_section(section_name, table)
        added_sections.append(section_name)


# def make_unique_values_table(data, report_dto, added_sections):
#     try:
#         unique_values_data = [[col, data[col].nunique()] for col in data.columns]
#         unique_values_headers = ['Column Name', 'Unique Values Count']
#         unique_values_column_widths = [440, 120]
#         unique_values_table = make_table(unique_values_data, unique_values_headers, unique_values_column_widths)
#
#         report_dto.add_section("Table_Unique Values Count", unique_values_table)
#         added_sections.append("Table_Unique Values Count")
#         logging.info("Unique values count table added.")
#     except Exception as e:
#         logging.error(f"Failed to create unique values count table: {e}")
#
#
