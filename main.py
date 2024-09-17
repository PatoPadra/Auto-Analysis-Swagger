from flask import Flask, request, send_from_directory, jsonify
import pandas as pd
import os
from Domain.PDFGenerator import PDFGenerator
from Domain.Get_data import fetch_data_from_sql
from Domain.Relatorio.GenericReport import GenericReport
from flasgger import Swagger
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
def hello():
    return "WELCOME"

# Utility function to handle adding sections safely
def add_section_safe(report_dto, section_name, method, *args, **kwargs):
    try:
        result = method(*args, **kwargs)
        if result:
            report_dto.add_section(section_name, result)
        else:
            report_dto.add_section(section_name, "Graph generation failed")
    except Exception as e:
        logging.error(f"Failed to generate '{section_name}' plot: {e}")
        report_dto.add_section(section_name, "Graph generation failed")


@app.route('/generate-pdf-generic', methods=['GET'])
def generate_pdf_generic():
    """
    Generate a generic PDF report
    ---
    parameters:
      - name: server
        in: query
        type: string
        required: true
        description: The server name
      - name: database
        in: query
        type: string
        required: true
        description: The database name
      - name: table
        in: query
        type: string
        required: true
        description: The table name
    responses:
      200:
        description: PDF generated successfully
      500:
        description: Error generating PDF
    """
    try:
        server = request.args.get('server')
        database = request.args.get('database')
        table = request.args.get('table')

        # Fetch data and unpack the tuple
        df, table_name = fetch_data_from_sql(server, database, table)

        # Debug print to inspect the DataFrame
        logging.debug(f"DataFrame columns: {df.columns}")
        logging.debug(f"DataFrame length: {len(df)}")

        generico = GenericReport()
        report_dto = generico.create_report(server, database, table_name)

        # Log the sections added to the report
        for section_title, content in report_dto.get_sections().items():
            logging.info(f"Section: {section_title}, Content: {content}")

        # PDF generation
        output_path = "output-generico.pdf"
        pdf_generator = PDFGenerator(output_path)
        pdf_file_path = pdf_generator.generate_pdf(report_dto)

        # Prepare to send the file
        directory = os.path.dirname(pdf_file_path)
        filename = os.path.basename(pdf_file_path)

        logging.debug(f"Directory: {directory}")  # Debugging output
        logging.debug(f"Filename: {filename}")  # Debugging output

        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        logging.error(e)  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
