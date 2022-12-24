import os.path

from .trivial import TrivialSearcher
from .search import Searcher
from .combo import L2Searcher
from config import Config


def get_searcher(config: Config):
    if config.test:
        return TrivialSearcher(config.database_path, "")
    elif config.searcher == "bm25":
        cache_path = os.path.join(config.cache_path, "bm25")
        return Searcher(config.database_path, cache_path, search_max_len=config.search_max_len)
    elif config.searcher == "l2":
        cache_path = os.path.join(config.cache_path, "l2")
        return L2Searcher(config.database_path, cache_path, search_max_len=config.search_max_len)
