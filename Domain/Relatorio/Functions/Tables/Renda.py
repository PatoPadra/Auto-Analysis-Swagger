# Functions/Tables/renda_table.py

import logging
from ....PDFGenerator import make_table
from ...Functions.Statics.Stats import  mean_and_count_by
def make_renda_table_more_than_three(data, report_dto, added_sections, prof_col, numeric_column='RENDA_PRESUMIDA'):
    try:
        ten_mean_high = mean_and_count_by(data, prof_col, numeric_column)
        ten_mean_high_filtered = ten_mean_high[ten_mean_high['count'] > 3]
        top_ten = ten_mean_high_filtered.nlargest(10, 'mean')
        table_data = [[row[prof_col], f"{row['mean']:.2f}", row['count']] for index, row in top_ten.iterrows()]
        headers = ['Profissão', 'Renda Média', 'Qtd']
        column_widths_renda = [420, 80, 50]  # Adjust column widths as needed
        renda_mean_table = make_table(table_data, headers, column_widths_renda)
        report_dto.add_section("Table_Top 10 prof_col by Renda", renda_mean_table)
        added_sections.append("Table_Top 10 prof_col by Renda")
        logging.info(f"Top 10 prof_col by average income table added.")
    except Exception as e:
        logging.error(f"Failed to create top 10 professions by average income table: {e}")


def make_greater_renda_table(data, report_dto, added_sections, prof_col, numeric_column='RENDA_PRESUMIDA'):
    try:
        ten_mean_high = mean_and_count_by(data, prof_col, numeric_column)
        top_ten = ten_mean_high.nlargest(10, 'mean')
        table_data = [[row[prof_col], f"{row['mean']:.2f}", row['count']] for index, row in top_ten.iterrows()]
        headers = ['Profissão', 'Renda Média', 'Qtd']
        column_widths_renda = [420, 80, 50]  # Adjust column widths as needed
        renda_mean_table = make_table(table_data, headers, column_widths_renda)
        report_dto.add_section("Table_Top 10 prof_col by Renda (No Filter)", renda_mean_table)
        added_sections.append("Table_Top 10 prof_col by Renda (No Filter)")
        logging.info(f"Top 10 prof_col by average income table added (No Filter).")
    except Exception as e:
        logging.error(f"Failed to create top 10 professions by average income table (No Filter): {e}")