from abc import abstractmethod
from typing import Generator, Iterable

from bs4 import BeautifulSoup, Tag

from ...models import SearchResult
from .general import GeneralSoupTemplate


class SearchableSoupTemplate(GeneralSoupTemplate):
    def search_novel(self, query) -> Iterable[SearchResult]:
        soup = self.get_search_page_soup(query)
        tags = self.select_search_items(soup)
        results = []
        for sr in self.process_search_results(tags):
            if sr:
                results.append(sr)
                if len(results) == 10:
                    break
        return results

    def process_search_results(self, tags: Iterable[Tag]) -> Generator[Tag, None, None]:
        """Process novel item tag and generates search results"""
        for tag in tags:
            if isinstance(tag, Tag):
                yield self.parse_search_item(tag)

    @abstractmethod
    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        """Get the search page soup from the query"""
        raise NotImplementedError()

    @abstractmethod
    def select_search_items(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        """Select novel items found in search page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_search_item(self, tag: Tag) -> SearchResult:
        """Parse a tag and return single search result"""
        raise NotImplementedError()
