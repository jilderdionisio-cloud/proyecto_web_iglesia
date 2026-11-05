from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HEADER_COLOR = colors.HexColor('#143c35')
LINE_COLOR = colors.HexColor('#dce4e3')


def period_label(start, end):
    if start and end:
        return f'Del {start.isoformat()} al {end.isoformat()}'
    if start:
        return f'Desde {start.isoformat()}'
    if end:
        return f'Hasta {end.isoformat()}'
    return 'Todos los registros'


def display(value):
    return f'{value:,.2f}' if isinstance(value, Decimal) else str(value)


def write_cell(sheet, row, column, value):
    cell = sheet.cell(row=row, column=column, value=value)
    if isinstance(value, str):
        # Un texto que empieza con "=" no debe interpretarse como fórmula al abrir el archivo.
        cell.data_type = 's'
    elif isinstance(value, Decimal):
        cell.number_format = '#,##0.00'
    return cell


def to_xlsx(report, church_name, start, end):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = report['title']
    write_cell(sheet, 1, 1, church_name).font = Font(bold=True, size=14)
    write_cell(sheet, 2, 1, report['title']).font = Font(bold=True)
    write_cell(sheet, 3, 1, period_label(start, end))
    for column, label in enumerate(report['columns'], start=1):
        write_cell(sheet, 5, column, label).font = Font(bold=True)
    for row_number, row in enumerate(report['rows'], start=6):
        for column, value in enumerate(row, start=1):
            write_cell(sheet, row_number, column, value)
    next_row = 7 + len(report['rows'])
    for label, value in report['totals']:
        write_cell(sheet, next_row, 1, label).font = Font(bold=True)
        write_cell(sheet, next_row, 2, value)
        next_row += 1
    for column, label in enumerate(report['columns'], start=1):
        longest = max([len(label), *(len(display(row[column - 1])) for row in report['rows'])])
        sheet.column_dimensions[get_column_letter(column)].width = min(longest + 3, 48)
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def to_pdf(report, church_name, start, end):
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm, title=report['title'], author=church_name)
    styles = getSampleStyleSheet()
    cell_style = styles['BodyText']
    cell_style.fontSize = 9
    cell_style.leading = 11
    header_style = styles['Heading5']
    header_style.textColor = colors.white
    header_style.spaceAfter = header_style.spaceBefore = 0

    def paragraphs(values, style):
        # Paragraph interpreta marcado XML: los datos de usuario se escapan.
        return [Paragraph(escape(display(value)), style) for value in values]

    table = Table(
        [paragraphs(report['columns'], header_style), *(paragraphs(row, cell_style) for row in report['rows'])],
        colWidths=[document.width / len(report['columns'])] * len(report['columns']),
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_COLOR),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    totals = ' · '.join(f'{escape(label)}: {escape(display(value))}' for label, value in report['totals'])
    document.build([
        Paragraph(escape(church_name), styles['Title']),
        Paragraph(escape(report['title']), styles['Heading2']),
        Paragraph(escape(period_label(start, end)), styles['Normal']),
        Spacer(1, 0.4 * cm),
        table,
        Spacer(1, 0.4 * cm),
        Paragraph(f'<b>{totals}</b>', styles['Normal']),
    ])
    return output.getvalue()
