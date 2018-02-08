#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler WebNovel novels and create epub & mobi files.

[WebNovel](https://www.webnovel.com) is a website of english translated
chinese/korean/japanese light novels. Also known as **Qidian**.
"""
import re
import sys
import requests
from os import path
from .binding import novel_to_kindle
from .helper import get_browser, save_chapter


class WebNovelCrawler:
    '''Crawler for WuxiaWorld'''

    def __init__(self, novel_id, start_chapter=None, end_chapter=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.novel_id = novel_id
        self.novel_name = 'Unknown'
        self.author_name = 'Sudipto Chandra'

        self.home_url = 'https://www.webnovel.com/book/' + novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter

        self.output_path = path.join('_novel', novel_id)
    # end def


    def start(self):
        '''start crawling'''
        self.crawl_csrf_token()
        # novel_to_kindle(self.output_path)
    # end def

    def crawl_csrf_token(self):
        '''get novel name and author'''
        print('Visiting:', self.home_url)
        session = requests.Session()
        cookies = session.cookies.get_dict()
        self.csrf = cookies['_csrfToken']
        print(cookies, self.csrf)
    # end def

    def crawl_chapters(self, browser):
        '''Crawl all chapters till the end'''
        url = self.start_url
        while url:
            print('Visiting:', url)
            browser.visit(url)
            next_link = browser.find_link_by_partial_text('Next Chapter')
            if not next_link:
                break
            # end if
            self.parse_chapter(browser)
            if url == self.end_url:
                break
            # end if
            url = next_link.first['href'].strip('/')
        # end while
    # end def

    def parse_chapter(self, browser):
        '''Parse the content of the chapter page'''
        url = browser.url.strip('/')
        chapter_no = re.search(r'\d+.?$', url).group().strip('/')
        vol_no = str(1 + (int(chapter_no) - 1) // 100)
        if re.match(r'.*-book-\d+-chapter-\d+', url):
            vol_no = re.search(r'-\d+-', url).group().strip('-')
        # end if
        articles = browser.find_by_css('div[itemprop="articleBody"] p')
        body = [x for x in articles][1:-1]
        chapter_title = body[0].text
        if re.match(r'Chapter \d+.*', body[1].text):
            chapter_title = body[1].text
            body = body[2:]
        else:
            body = body[1:]
        # end if
        body = ''.join(['<p>' + x.html + '</p>' for x in body if x.text.strip()])
        # save data
        save_chapter({
            'url': url,
            'novel': self.novel_name,
            'chapter_no': chapter_no,
            'chapter_title': chapter_title,
            'volume_no': vol_no,
            'body': '<h1>%s</h1>%s' % (chapter_title, body)
        }, self.output_path)
    # end def
# end class

if __name__ == '__main__':
    WebNovelCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None
    ).start()
# end if
