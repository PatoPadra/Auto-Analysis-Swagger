from flask import send_from_directory
from Domain.PDFGenerator import PDFGenerator
import os

def register_controllers(app):
    @app.route('/download/lailao')
    def download_lailao():
        filename = PDFGenerator.create_pdf('lailao')
        directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Domain'))
        print("Directory Path:", directory_path)
        print("Filename:", filename)
        return send_from_directory(path=directory_path, filename=filename, as_attachment=True)

    @app.route('/download/score')
    def download_score():
        filename = PDFGenerator.create_pdf('score')
        directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Domain'))
        return send_from_directory(path=directory_path, filename=filename, as_attachment=True)


#%%
