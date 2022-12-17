from .trivial import TrivialSearcher
from .search import Searcher
from config import Config


def get_searcher(config: Config):
    if config.test:
        return TrivialSearcher(config.database_path, config.index_path)
    else:
        return Searcher(config.database_path, config.index_path)
