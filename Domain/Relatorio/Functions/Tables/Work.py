

import logging
from ....PDFGenerator import make_table
from ...Functions.Statics.Stats import  first_tenth

def make_work_table(data, report_dto, added_sections, column):
    try:
        ten_prof_max = first_tenth(data, column)
        table_data = [[profession, count] for profession, count in ten_prof_max.items()]
        headers = ['Profissão', 'Qtd']
        column_widths_prof = [520, 80]  # Adjust column widths as needed
        professions_table = make_table(table_data, headers, column_widths_prof)
        report_dto.add_section("Table_Top 10 prof", professions_table)
        added_sections.append("Table_Top 10 prof")
        logging.info(f"Table_Top 10 prof table added.")
    except Exception as e:
        logging.error(f"Failed to create top 10 professions table: {e}")
