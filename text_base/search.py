from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import pymorphy2
import json


@dataclass
class SearchAnswer:
    documents: List[int]


class Searcher:
    tf_index: Dict[str, List[Tuple[int, int]]]
    idf_index: Dict[str, float]

    def __init__(self, base_path: str, index_path: str):
        self.create_structure()

    def create_structure(self):
        """
        Создает индекс документов
        """
        pass

    def find(self, query) -> SearchAnswer:
        pass


SEARCHER: Optional[Searcher] = None


def get_searcher(base_path: str) -> Searcher:
    global SEARCHER
    if SEARCHER is None:
        SEARCHER = Searcher(base_path)

    return SEARCHER


# example
if __name__ == "__main__":
    searcher = Searcher("songs")

    print(searcher.find("kek lol"))
