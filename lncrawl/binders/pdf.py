#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import io
import logging
import os
import re
from datetime import datetime

from progress.bar import IncrementalBar

logger = logging.getLogger('PDF_BINDER')

try:
    from weasyprint import HTML
except Exception:
    import traceback
    logger.debug(traceback.format_exc())
# end try


class PdfBuilder:
    def __init__(self, app, chapters, volume=''):
        self.app = app
        self.volume = volume
        self.chapters = chapters
        self.crawler = app.crawler
        self.file_name = (app.good_file_name + ' ' + volume).strip()
        self.book_title = (app.crawler.novel_title + ' ' + volume).strip()
    # end def

    def make_metadata(self):
        # Make html page content
        html = '''
            <title>{title}</title>
            <meta name="author">{author}</meta>
            <meta name="authors">Lightnovel Crawler</meta>
            <meta name="description">Original source: {novel_url}</meta>
            <meta name="generator">Lightnovel Crawler</meta>
        '''.format(
            title=self.book_title or 'N/A',
            author=self.crawler.novel_author or 'N/A',
            novel_url=self.crawler.novel_url,
        )
        return html
    # end def

    def create_intro(self):
        logger.info('Creating first page')
        source_url = self.crawler.home_url or 'Unknown'
        github_url = 'https://github.com/dipu-bd/lightnovel-crawler'

        intro_html = '<div style="%s">' % ';'.join([
            'height: 9in',
            'display: flex',
            'flex-direction: column',
            'justify-content: space-between',
            'text-align: center',
        ])

        intro_html += '''
            <div style="width: 6in">
                <h1>%s</h1>
                <h3>%s</h3>
            </div>
        ''' % (
            self.book_title or 'N/A',
            self.crawler.novel_author or 'N/A',
        )

        if self.app.book_cover:
            logger.info('Adding cover: %s', self.app.book_cover)
            ext = self.app.book_cover.split('.')[-1]
            with open(self.app.book_cover, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode("utf-8")
            # end with
            intro_html += '<div style="%s">&nbsp;</div>' % ';'.join([
                'height: 4in',
                'width: 6in',
                'background-size: contain',
                'background-repeat: no-repeat',
                'background-position: center',
                'background-image: url(data:image/%s;base64,%s)' % (ext, encoded)
            ])
        # end if

        intro_html += '''
        <div style="width: 6in">
            <p><b>Source:</b> <a href="%s">%s</a></p>
            <p><i>Generated by <b><a href="%s">Lightnovel Crawler</a></b></i></p>
        </div>''' % (source_url, source_url, github_url)

        intro_html += '</div>'

        return intro_html
    # end def

    def bind(self):
        logger.debug('Binding %s.pdf', self.file_name)
        pdf_path = os.path.join(self.app.output_path, 'pdf')
        os.makedirs(pdf_path, exist_ok=True)

        all_pages = []

        bar = IncrementalBar('Adding chapters to PDF', max=len(self.chapters))
        bar.start()

        if os.getenv('debug_mode') == 'yes':
            bar.next = lambda: None  # Hide in debug mode
        # end if

        html = HTML(string=self.create_intro())
        all_pages += html.render().pages
        logger.info('Added intro page')

        for chapter in self.chapters:
            html_string = chapter['body']
            html = HTML(string=html_string)
            all_pages += html.render().pages
            logger.info('Added chapter %d', chapter['id'])
            bar.next()
        # end for

        bar.finish()

        html = HTML(string=self.make_metadata())
        combined = html.render().copy(all_pages)

        output_file = os.path.join(pdf_path, '%s.pdf' % self.file_name)
        combined.write_pdf(output_file)
        print('Created: %s.pdf' % self.file_name)

        return output_file
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
            ).bind()
            pdf_files.append(book)
        # end if
    # end for
    return pdf_files
# end def
