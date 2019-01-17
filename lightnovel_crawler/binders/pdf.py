#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import io
import os
import logging
from bs4 import BeautifulSoup
import reportlab.platypus as pdf
from reportlab.lib.units import inch
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger('PDF_BINDER')


class PdfBuilder:
    elements = []
    styles = getSampleStyleSheet()

    def __init__(self, app, chapters, volume=''):
        self.app = app
        self.chapters = chapters
        self.crawler = app.crawler
        self.book_title = (self.crawler.novel_title + ' ' + volume).strip()
    # end def

    def create_book(self):
        logger.debug('Binding %s.pdf', self.book_title)
        pdf_path = os.path.join(self.app.output_path, 'pdf')
        file_path = os.path.join(pdf_path, self.book_title + '.pdf')
        logger.debug('Writing %s', file_path)
        os.makedirs(pdf_path, exist_ok=True)

        # , pagesize = reportlab.lib.pagesizes.portrait(reportlab.lib.pagesizes.A4))
        self.book = pdf.SimpleDocTemplate(file_path)
        self.book.lang = 'en'
        self.book.title = self.book_title
        self.book.author = 'Lightnovel Crawler'
    # end def

    def pre(self, text):
        p = pdf.Preformatted(text, style=self.styles['Code'])
        self.elements.append(p)
    # end def

    def create_intro(self):
        self.elements += [
            pdf.Spacer(0, 0.25 * inch),
            pdf.Paragraph(
                self.crawler.novel_title or 'N/A',
                style=self.styles['Title']
            ),
            pdf.Spacer(0, 0.1 * inch),
            pdf.Table(
                [[self.crawler.novel_author or 'N/A']],
                style=pdf.TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('SIZE', (0, 0), (-1, -1), 12),
                ]),
            ),
            pdf.Spacer(0, 0.5 * inch),
        ]

        if self.app.book_cover:
            self.elements += [
                pdf.Image(self.app.book_cover, height=5 * inch)
            ]
        else:
            self.elements += [pdf.Spacer(0, 5 * inch)]
        # end if

        self.elements += [
            pdf.Spacer(0, 0.5 * inch),
            pdf.Table(
                [['Generated by <Lightnovel Crawler>'], [
                    'https://github.com/dipu-bd/lightnovel-crawler']],
                style=pdf.TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]),
            ),
        ]
        self.elements += [pdf.PageBreak()]
    # end def

    def create_chapter(self, content):
        for tag in content.children:
            if not tag.name:
                self.elements += [
                    pdf.Spacer(0, 0.15 * inch),
                    pdf.Paragraph(str(tag), self.styles['Normal']),
                ]
            elif re.match(r'h\d', tag.name):
                self.elements += [
                    pdf.Paragraph(tag.text, self.styles[tag.name]),
                ]
            elif tag.name == 'p':
                self.elements += [
                    pdf.Spacer(0, 0.15 * inch),
                    pdf.Paragraph(tag.text, self.styles['Normal']),
                ]
                # elif re.match(r'b|strong|label', tag.name):
                #     run = paragraph.add_run(tag.text)
                #     run.bold = True
                # elif re.match(r'i|em|cite', tag.name):
                #     run = paragraph.add_run(tag.text)
                #     run.italic = True
                # elif re.match(r'u', tag.name):
                #     run = paragraph.add_run(tag.text)
                #     run.underline = True
                # elif re.match(r'sub', tag.name):
                #     run = paragraph.add_run(tag.text)
                #     run.font.subscript = True
                # elif re.match(r'sup', tag.name):
                #     run = paragraph.add_run(tag.text)
                #     run.font.superscript = True
                # elif re.match(r'pre|code|kdb', tag.name):
                #     run = paragraph.add_run(tag.text)
                #     run.font.outline = True
                # else:
                # paragraph.add_run(tag.text)
            # end if
        # end for
        self.elements += [pdf.PageBreak()]
    # end def

    def pagenum_generator(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 10)
        canvas.drawCentredString(
            4.135 * inch, 11.0 * inch, '〈 %s 〉' % doc.title)

        canvas.setFont('Times-Bold', 9)
        canvas.drawCentredString(4.135 * inch, 0.75 * inch,
                                 'Page %d' % canvas.getPageNumber())
    # end def

    def create_toc(self):
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            ParagraphStyle(fontName='Times-Bold', fontSize=14, name='Heading1',
                           leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
            ParagraphStyle(fontSize=12, name='Heading2',
                           leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=12),
        ]
        self.elements += [
            self.toc,
            pdf.PageBreak(),
        ]
    # end def

    def bind(self):
        self.create_book()
        self.create_intro()
        # self.create_toc()

        for chapter in self.chapters:
            soup = BeautifulSoup(chapter['body'], 'lxml')
            self.create_chapter(soup.find('body'))
        # end for

        self.book.multiBuild(
            self.elements,
            onLaterPages=self.pagenum_generator
        )

        logger.warn('Created: %s.pdf', self.book_title)
        return self.book.filename
    # end def
# end class


def make_pdfs(app, data):
    pdf_files = []
    for vol in data:
        if len(data[vol]) > 0:
            book = PdfBuilder(
                app,
                volume=vol,
                chapters=data[vol],
            )
            pdf_files.append(book.bind())
        # end if
    # end for
    return pdf_files
# end def
