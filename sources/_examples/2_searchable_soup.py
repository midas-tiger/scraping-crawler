# -*- coding: utf-8 -*-
"""
# TODO: Read the TODOs carefully and remove all existing comments in this file.

This is a sample using the SearchableSoupTemplate as the template. This template
provides a wrapper around the GeneralSoupTemplate to support search.

Put your source file inside the language folder. The `en` folder has too many
files, therefore it is grouped using the first letter of the domain name.
"""
import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag

from lncrawl.models import SearchResult
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


# TODO: You can safely delete all [OPTIONAL] methods if you do not need them.
class MyCrawlerName(SearchableSoupTemplate):
    # TODO: [REQUIRED] Provide the URLs supported by this crawler.
    base_url = ["http://sample.url/"]

    # TODO: [OPTIONAL] Set True if this crawler is for manga/manhua/manhwa.
    has_manga = False

    # TODO: [OPTIONAL] Set True if this source contains machine translations.
    has_mtl = False

    # TODO: [OPTIONAL] This is called before all other methods.
    def initialize(self) -> None:
        # You can customize `TextCleaner` and other necessary things.
        pass

    # TODO: [OPTIONAL] This is called once per session before searching and fetching novel info.
    def login(self, username_or_email: str, password_or_token: str) -> None:
        # Examples:
        # - https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py
        # - https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/ranobes.py
        pass

    # TODO: [OPTIONAL] If it is necessary to logout after session is finished, you can implement this.
    def logout(self):
        pass

    # TODO: [REQUIRED] Get the search page soup from the query
    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        # The query here is the input from user.
        #
        # return self.post_soup(
        #     f"{self.home_url}search/", data={"searchkey": query.lower()}
        # )
        pass

    # TODO: [REQUIRED] Select novel items found in search page soup
    def select_search_items(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        # The soup here is the result of `self.get_soup(self.get_search_page_soup(query))`
        #
        # Example: yield from soup.select(".col-content .con .txt h3 a")
        pass

    # TODO: [REQUIRED] Parse a tag and return single search result
    def parse_search_item(self, tag: Tag) -> SearchResult:
        # The tag here comes from self.select_search_items
        #
        # Example:
        # return SearchResult(
        #     title=tag.text.strip(),
        #     url=self.absolute_url(tag["href"]),
        # )
        pass

    # TODO: [REQUIRED] Parse and return the novel title
    def parse_title(self, soup: BeautifulSoup) -> str:
        # The soup here is the result of `self.get_soup(self.novel_url)`
        pass

    # TODO: [REQUIRED] Parse and return the novel cover
    def parse_cover(self, soup: BeautifulSoup) -> str:
        # The soup here is the result of `self.get_soup(self.novel_url)`
        pass

    # TODO: [REQUIRED] Parse and return the novel authors
    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        # The soup here is the result of `self.get_soup(self.novel_url)`
        #
        # Example 1: <a single author example>
        #   tag = soup.find("strong", string="Author:")
        #   assert tag
        #   yield tag.next_sibling.text.strip()
        #
        # Example 2: <multiple authors example>
        #   for a in soup.select(".m-imgtxt a[href*='/authors/']"):
        #       yield a.text.strip()
        pass

    # TODO: [REQUIRED] Parse and set the volumes and chapters
    def parse_chapter_list(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        # The soup here is the result of `self.get_soup(self.novel_url)`
        pass

    # TODO: [OPTIONAL] Return the index in self.chapters which contains a chapter URL
    def index_of_chapter(self, url: str) -> int:
        # To get more help, check the default implemention in the `Crawler` class.
        pass
