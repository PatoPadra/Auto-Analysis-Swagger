from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

class PDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path

    def generate_pdf(self, report_dto):
        c = canvas.Canvas(self.output_path, pagesize=letter)
        margin_left = 1 * cm
        margin_top = 1 * cm
        text_height = 750 - margin_top

        def add_text_section(title, content):
            nonlocal text_height
            lines = content.split('\n')
            estimated_text_height = len(lines) * 15 + 20

            if text_height - estimated_text_height < 50:
                c.showPage()
                text_height = 750 - margin_top

            text_height -= 20
            c.setFont("Helvetica-Bold", 14)
            title_width = c.stringWidth(title, "Helvetica-Bold", 14)
            title_x = (letter[0] - title_width) / 2
            c.drawString(title_x, text_height, title)
            c.line(title_x, text_height - 2, title_x + title_width, text_height - 2)
            text_height -= 40

            c.setFont("Helvetica", 12)
            for line in lines:
                if text_height - 15 < 60:
                    c.showPage()
                    text_height = 750 - margin_top
                c.drawString(margin_left, text_height, line.strip())
                text_height -= 15

        for section_key in report_dto.order:
            content = report_dto.sections[section_key]

            if isinstance(content, Table):
                estimated_table_height = len(content._cellvalues) * 20 + 20

                if text_height - estimated_table_height < 50:
                    c.showPage()
                    text_height = 750 - margin_top

                c.setFont("Helvetica-Bold", 14)
                title_width = c.stringWidth(section_key, "Helvetica-Bold", 14)
                title_x = (letter[0] - title_width) / 2
                c.drawString(title_x, text_height, section_key)
                c.line(title_x, text_height - 2, title_x + title_width, text_height - 2)
                text_height -= 40

                table_position = text_height - estimated_table_height
                content.wrapOn(c, letter[0] - 2 * margin_left, letter[1])
                content.drawOn(c, margin_left, table_position)
                text_height = table_position - 20

            elif 'Graph_' in section_key and isinstance(content, str) and content.endswith('.png'):
                if text_height - 300 < 50:
                    c.showPage()
                    text_height = 750 - margin_top
                img_path = os.path.abspath(content)
                if os.path.exists(img_path):
                    img_width = 520
                    img_height = 300
                    img_x = (letter[0] - img_width) / 2
                    img_y = text_height - img_height - 20
                    c.drawImage(img_path, img_x, img_y, width=img_width, height=img_height)
                    text_height = img_y - 10

            elif isinstance(content, str):
                add_text_section(section_key, content)

        c.save()
        return self.output_path


def make_table(data, headers, column_widths):
    # Prepare data with truncated text
    truncated_data = []
    for row in data:
        truncated_row = [
            truncate_text(str(cell), width, 'Helvetica', 10)
            for cell, width in zip(row, column_widths)
        ]
        truncated_data.append(truncated_row)

    table_data = [headers] + truncated_data
    table = Table(table_data, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))

    return table

def truncate_text(text, max_width, font_name, font_size):
    ellipsis = '...'
    text_width = stringWidth(text, font_name, font_size)
    ellipsis_width = stringWidth(ellipsis, font_name, font_size)

    if text_width <= max_width:
        return text
    else:
        truncated_text = ''
        for char in text:
            if stringWidth(truncated_text + char + ellipsis, font_name, font_size) <= max_width:
                truncated_text += char
            else:
                break
        return truncated_text + ellipsis

def calculate_column_widths(data, headers, font_name='Helvetica', font_size=10):
    max_widths = []

    # Calculate initial max widths from headers
    for header in headers:
        width = pdfmetrics.stringWidth(str(header), font_name, font_size) + 10  # Convert headers to string to avoid type issues
        max_widths.append(width)

    # Adjust widths based on the content in data
    for row in data:
        for index, item in enumerate(row):
            item_width = pdfmetrics.stringWidth(str(item), font_name, font_size) + 10  # Ensure items are strings
            if item_width > max_widths[index]:
                max_widths[index] = item_width

    return max_widths

def make_split_table(data, headers, column_widths, max_rows_per_page=30):
    """
    Create a table that splits across multiple pages if necessary.

    :param data: List of lists representing the table data
    :param headers: List of headers for the table
    :param column_widths: List of column widths
    :param max_rows_per_page: Maximum number of rows that can fit on one page
    :return: List of tables (one per page)
    """

    tables = []
    num_rows = len(data)
    num_pages = (num_rows // max_rows_per_page) + 1

    for i in range(num_pages):
        start_row = i * max_rows_per_page
        end_row = start_row + max_rows_per_page
        chunk = data[start_row:end_row]

        # Include headers on each page
        chunk_with_headers = [headers] + chunk

        # Create the table for this chunk
        table = Table(chunk_with_headers, colWidths=column_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        tables.append(table)

    return tables
