# -*- coding: utf-8 -*-
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.mywuxiaworld.com/search/result.html?searchkey=%s'


class MyWuxiaWorldCrawler(Crawler):
    base_url = [
        'https://www.mywuxiaworld.com/',
        'https://m.mywuxiaworld.com/',
    ]

    def initialize(self):
        self.home_url = 'https://www.mywuxiaworld.com/'
    # end def

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        soup = self.get_soup(search_url % query)

        results = []
        for li in soup.select('div.pt-rank-detail a'):
            a = li.select_one('a.size18.color2')['href']
            title = li.select_one('a.size18.color2').text
            author = li.select_one('span.mr30 a').text

            results.append({
                'title': title,
                'url': self.absolute_url(a['href']),
                'info': author,
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('a.color2.bold').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('span.color5').text.strip()
        logger.info('Novel title: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('img.pt-bookdetail-img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select('div.pt-chapter-cont-detail.full a')

        for a in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.select_one('span').text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.info('%d chapters and %d volumes found',
                    len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        chapter['title'] = soup.select_one('a.color7').text.strip()

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        contents = soup.select('div.pt-read-cont p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def

# end class
