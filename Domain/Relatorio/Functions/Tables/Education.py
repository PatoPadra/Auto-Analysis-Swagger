import logging
from ....PDFGenerator import make_table


def make_education_table(data, report_dto, added_sections, column='ESCOLARIDADE'):
    try:
        education_counts = data[column].value_counts()
        education_data = [[level, count] for level, count in education_counts.items()]
        education_headers = ['Nível de educação', 'Quantidade']
        education_column_widths = [500, 80]
        education_table = make_table(education_data, education_headers, education_column_widths)
        report_dto.add_section("Table_Education Levels", education_table)
        added_sections.append("Table_Education Levels")
        logging.info("Education levels table added.")
    except Exception as e:
        logging.error(f"Failed to create education data table: {e}")
