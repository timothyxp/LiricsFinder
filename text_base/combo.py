import os.path

from .base import BaseSearcher, SearchAnswer
from .search import Searcher


class L2Searcher(BaseSearcher):
    def __init__(self, base_path: str, cache_path: str):
        super().__init__(base_path, cache_path)

        text_searcher_cache = os.path.join(cache_path, "text_searcher")
        self.text_searcher = Searcher(base_path, text_searcher_cache)

        author_searcher_cache = os.path.join(cache_path, "author_searcher")
        self.author_searcher = Searcher(base_path, author_searcher_cache)

    def find(self, query: str) -> SearchAnswer:
        pass
