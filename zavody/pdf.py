# coding: utf-8
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageBreak, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont


from hanes.settings import STATICFILES_DIRS
pdfmetrics.registerFont(
    TTFont('Arial', STATICFILES_DIRS[0] + '/fonts/arial.ttf'))


class PdfPrint:

    # initialize class
    def __init__(self, buffer):
        self.buffer = buffer
        self.pageSize = A4
        self.width, self.height = self.pageSize

# ---------------------------------------------------
    def addPageNumber(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = "str. %s" % page_num
        canvas.setFontSize(10)
        canvas.setFillColorRGB(.6, .6, .6)
        canvas.drawRightString(20.8*cm, .2*cm, text)

# ---------------------------------------------------
    def sheet(self, tables, widths=None, right_aligned=[]):
        # set some characteristics for pdf document
        doc = SimpleDocTemplate(
            self.buffer,
            rightMargin=5,
            leftMargin=5,
            topMargin=15,
            bottomMargin=15,
            pagesize=self.pageSize)

        styles = getSampleStyleSheet()
        # add custom paragraph style
        styles['Title'].fontName = 'Arial'
        styles.add(ParagraphStyle(
            name="TableHeader", fontSize=10,
            alignment=TA_CENTER, fontName='Arial'))
        styles.add(ParagraphStyle(
            name='Arial', fontName='Arial', fontSize=10))
        styles.add(ParagraphStyle(
            name='Right', fontName='Arial', fontSize=10, alignment=TA_RIGHT))

        V_LIST = 277
        v_akt = 0.0
        data = []
        for table in tables:
            # table['rows'] *= 2

            # NOVA STRANKA / ODRADKOVANI
            v_tab = 10.0 + len(table['headers']) * 10.0 + len(table['rows']) * 6.3
            if v_akt != 0.0:
                # prvni podminka pro povoleni nenuceneho deleni tabulek
                if (v_akt <= V_LIST * 0.5) or (v_akt + v_tab + 19 <= V_LIST):
                    data.append(Spacer(1, 50))
                    v_akt += 19
                else:
                    data.append(PageBreak())
                    v_akt = 0.0
            v_akt = (v_akt + v_tab) % V_LIST

            # TITULEK
            data.append(Paragraph(table['title'], styles['Title']))
            data.append(Spacer(1, 5))

            # TABULKA
            headers = [
                [Paragraph(unicode(value), styles['TableHeader']) for value in row]
                for row in table['headers']
            ]

            rows = [
                [Paragraph(unicode(value), styles['Right' if i in right_aligned else 'Arial']) for i, value in enumerate(row)]
                for row in table['rows']
            ]

            if widths:
                wh_table = Table(headers + rows, colWidths=[val * cm for val in widths])
            else:
                wh_table = Table(headers + rows)
            wh_table.setStyle(TableStyle([
                ('INNERGRID', (0, 0), (-1, -1), 0.1, colors.gray),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.gray),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('BACKGROUND',
                    (0, 0), (-1,  len(headers) - 1),
                    colors.Color(.8, .8, .8))])),
            data.append(wh_table)

        doc.build(data, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)

        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf
