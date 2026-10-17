#!/usr/bin/env python3
"""Render the current individual task cards as phase-specific GoodNotes sheets.

The supplied original workbooks are retained. Only derived GoodNotes_Phase files
are rebuilt. Task operators, text, references and continuous numbers come from
lesson-data.js; no answer or personal progress is included.
"""
from __future__ import annotations
import argparse
import base64
import html as escaping
import json
from pathlib import Path


def prepare(root):
    from lxml import html
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    import fitz
    from transfer_scorm_design import payload
    from individualize_scorm_tasks import PHASES, normalized
    fonts = Path('/usr/share/fonts/truetype/dejavu')
    for name, file in [('TaskSans', 'DejaVuSans.ttf'), ('TaskSans-Bold', 'DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily('TaskSans', normal='TaskSans', bold='TaskSans-Bold', italic='TaskSans', boldItalic='TaskSans-Bold')
    data = payload((root / 'lesson-data.js').read_bytes())
    text_style = ParagraphStyle('task', fontName='TaskSans', fontSize=10.5, leading=15, textColor=colors.HexColor('#173a63'), spaceAfter=8)
    ref_style = ParagraphStyle('reference', parent=text_style, fontSize=8.5, leading=12, textColor=colors.HexColor('#476475'))
    head_style = ParagraphStyle('heading', parent=text_style, fontName='TaskSans-Bold', fontSize=14, leading=19, spaceAfter=11)
    number_style = ParagraphStyle('number', parent=text_style, fontName='TaskSans-Bold', textColor=colors.white, alignment=1, fontSize=14, leading=22)
    gn = ImageReader(str(root / 'assets/goodnotes.png'))

    def inline(node):
        value = escaping.escape(node.text or '')
        for child in node:
            if child.tag in {'script', 'style', 'input', 'button', 'img'}:
                rendered = ''
            elif child.tag == 'br':
                rendered = '<br/>'
            else:
                rendered = inline(child)
                if child.tag in {'b', 'strong'}:
                    rendered = '<b>' + rendered + '</b>'
            value += rendered + escaping.escape(child.tail or '')
        return value

    def paragraphs(node):
        if node.tag in {'ul', 'ol'}:
            for item in node:
                yield Paragraph(inline(item), text_style, bulletText='\u2022')
        elif node.tag in {'p', 'div', 'section'}:
            if node.tag != 'p' and any(c.tag in {'p', 'ul', 'ol', 'div'} for c in node):
                for child in node:
                    yield from paragraphs(child)
            elif normalized(node.text_content()):
                yield Paragraph(inline(node), ref_style if 'book-line' in node.get('class', '') else text_style)

    class Sheet(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            if not isinstance(flowable, PageBreak):
                self.last_y = self.frame._y

        def handle_pageEnd(self):
            self.workbook_end(self.canv, self)
            super().handle_pageEnd()

    generated = []
    for phase in PHASES:
        document = html.fragment_fromstring(data['pages'][phase + '.html'], create_parent='div')
        for panel in document.xpath('.//*[@data-mode-panel]'):
            mode = panel.get('data-mode-panel')
            cards = panel.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," assignment-frame ")]')
            path = root / f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf'
            story = []
            for i, card in enumerate(cards):
                if i:
                    story.append(PageBreak())
                table = Table([[Paragraph(card.get('data-task-number'), number_style), Paragraph('Aufgabe ' + card.get('data-task-number'), head_style)]], colWidths=[32, 450])
                table.setStyle(TableStyle([('BACKGROUND', (0,0),(0,0),colors.HexColor('#009bd9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(1,0),(1,0),13),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
                story.extend([table, Spacer(1, 10)])
                body = card.xpath('./*[contains(concat(" ",normalize-space(@class)," ")," assignment-body ")]')[0]
                for child in body:
                    story.extend(paragraphs(child))
            def start(canvas, doc):
                doc.last_y = 746
                canvas.saveState()
                canvas.setFillColor(colors.HexColor('#173a63'))
                canvas.setFont('TaskSans-Bold', 9)
                canvas.drawString(42, 804, data['id'] + ' | ' + data['pageTitles'][phase + '.html'] + ' | Weg ' + mode)
                canvas.setFont('TaskSans', 8)
                canvas.drawString(42, 788, data['title'])
                canvas.setStrokeColor(colors.HexColor('#bce7fc'))
                canvas.line(42, 780, 553, 780)
                canvas.drawImage(gn, 535, 799, width=17, height=17, mask='auto')
                canvas.restoreState()
            def end(canvas, doc):
                canvas.saveState()
                y = doc.last_y - 28
                if y > 105:
                    canvas.setFont('TaskSans', 8)
                    canvas.setFillColor(colors.HexColor('#617988'))
                    canvas.drawString(42, y, 'Notizen und Bearbeitung')
                    canvas.setStrokeColor(colors.HexColor('#dce8ee'))
                    y -= 20
                    while y > 65:
                        canvas.line(42, y, 553, y)
                        y -= 20
                canvas.setFont('TaskSans', 8)
                canvas.setFillColor(colors.HexColor('#617988'))
                canvas.drawString(42, 35, 'BBS 1 Aurich | BioCasa | ' + data['pageTitles'][phase + '.html'])
                canvas.drawRightString(553, 35, str(doc.page))
                canvas.restoreState()
            pdf = Sheet(str(path), pagesize=(595.276, 841.89), leftMargin=42, rightMargin=42, topMargin=83, bottomMargin=60, title=data['title'] + ' - ' + data['pageTitles'][phase + '.html'], author='BBS 1 Aurich')
            pdf.workbook_end = end
            pdf.build(story, onFirstPage=start, onLaterPages=start)
            with fitz.open(path) as check:
                text = normalized(' '.join(page.get_text() for page in check).replace('\u2022', ''))
                for card in cards:
                    assert 'Aufgabe ' + card.get('data-task-number') in text, path
                    body = card.xpath('./*[contains(@class,"assignment-body")]')[0]
                    for child in body:
                        expected = normalized(child.text_content())
                        assert expected in text, (path, expected[:160])
            encoded = base64.b64encode(path.read_bytes()).decode()
            (root / f'goodnotes-phase-{phase}-W{mode}.js').write_text('window.GOODNOTES_PHASES=Object.assign(window.GOODNOTES_PHASES||{},' + json.dumps({phase + ':' + mode: encoded}) + ');\n')
            generated.append(path)
    return generated


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    print('Generated', len(prepare(args.folder)), 'phase workbooks')
