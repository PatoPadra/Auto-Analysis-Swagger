from flask import Flask, request, send_from_directory, jsonify
import pandas as pd
import os
from Domain.PDFGenerator import PDFGenerator
from Domain.Get_data import fetch_data_from_sql
from Domain.Relatorio.GenericReport import GenericReport
from Domain.Adding_safe import add_section_safe
from flasgger import Swagger
from flask import render_template
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
swagger = Swagger(app)

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello():
    return "WELCOME"

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/generate-pdf-generic', methods=['GET'])
def generate_pdf_generic():
    """
    Generate a generic PDF report from the server
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

        generico = GenericReport()
        report_data, report_dto = generico.create_report(df)

        # Generate the PDF
        output_path = "output-generico.pdf"
        pdf_generator = PDFGenerator(output_path)
        pdf_file_path = pdf_generator.generate_pdf(report_dto)

        return send_from_directory(os.path.dirname(pdf_file_path), os.path.basename(pdf_file_path), as_attachment=True)

    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500


def convert_to_serializable(report_data):
    """
    Convert non-serializable objects in the report data to serializable formats.
    """
    for key, value in report_data.items():
        if isinstance(value, pd.DataFrame):  # Example: Convert DataFrame to dictionary
            report_data[key] = value.to_dict(orient='records')  # Convert DataFrame to list of dictionaries
        elif hasattr(value, 'to_dict'):  # If the object has a `to_dict` method
            report_data[key] = value.to_dict()
        else:
            # Fallback: Convert other objects to string
            report_data[key] = str(value)
    return report_data


@app.route('/generate-json-generic', methods=['GET'])
def generate_json_generic():
    """
    Generate a generic report and return it as JSON from the server
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
        description: JSON report generated successfully
      500:
        description: Error generating report
    """
    try:
        server = request.args.get('server')
        database = request.args.get('database')
        table = request.args.get('table')

        # Fetch data from the server
        df, table_name = fetch_data_from_sql(server, database, table)

        generico = GenericReport()
        report_dto = generico.create_report(df)  # Only one return value now

        # Convert the report sections to a dictionary to return as JSON
        report_data = report_dto.get_sections()

        # Convert non-serializable objects in the report data
        serializable_report_data = convert_to_serializable(report_data)

        # Return the generated report as JSON
        return jsonify(serializable_report_data), 200

    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500


@app.route('/upload-file', methods=['POST'])
def upload_file():
    """
    Upload a CSV, Excel, or TXT file and run analysis on it
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The file to upload (CSV, Excel, or TXT)
    responses:
      200:
        description: File processed successfully and PDF generated
      400:
        description: Error processing the file
      500:
        description: Server error during processing
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    # Secure the filename and save the file to the upload folder
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Check if the file is CSV, Excel, or TXT and read it accordingly
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(filepath)
        elif filename.endswith('.txt'):
            df = pd.read_csv(filepath, delimiter='\t')  # Assuming tab-delimited for TXT
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Run your analysis on the dataframe (df)
        generico = GenericReport()
        report_dto = generico.create_report(data=df, table=filename)  # Passing the dataframe

        # Generate the PDF
        output_path = "output-uploaded-file.pdf"
        pdf_generator = PDFGenerator(output_path)
        pdf_file_path = pdf_generator.generate_pdf(report_dto)

        # Send the generated PDF back to the client
        return send_from_directory(os.path.dirname(pdf_file_path), os.path.basename(pdf_file_path), as_attachment=True)

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
